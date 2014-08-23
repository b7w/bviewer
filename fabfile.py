# -*- coding: utf-8 -*-
import json
from os import path
from functools import partial

from fabric.decorators import task
from fabric.context_managers import cd, settings, hide, shell_env
from fabric.contrib.files import exists, upload_template
from fabric.operations import sudo, put


def load_config():
    class Config(dict):
        __getattr__ = dict.__getitem__

    conf = Config(
        secret_key=NotImplemented,
        domains=NotImplemented,
        revision='default',
        user='bviewer',
        source_path='/home/bviewer/source',
        config_path='/home/bviewer/configs',
        log_path='/home/bviewer/logs',
        run_path='/var/run/bviewer',
        cache_path='/home/bviewer/cache',
        share_path='/home/bviewer/share',
    )
    with open('configs/deploy.json') as f:
        result = json.load(f)
        conf.update(result)
    return conf


config = load_config()

# Helpers
upload = partial(upload_template, context=config, use_jinja=True, template_dir='configs', use_sudo=True)


def pip_env():
    return shell_env(PYTHON_EGG_CACHE='/home/{0}/.python-eggs'.format(config.user))


def stat(path, user=config.user, group=config.user, mode=640):
    sudo('chown -R {0}:{1} {2}'.format(user, group, path))
    sudo('find {0} -type f -exec chmod {1} {{}} +'.format(path, mode))


def mkdir(path, user=config.user, group=config.user, mode=640):
    if not exists(path):
        sudo('mkdir --parents {0}'.format(path))
        stat(path, user, group, mode)


# Tasks
@task
def install_libs():
    packages = ['build-essential', 'htop', 'mercurial', 'git', 'python3-dev', 'python3-pip', ]
    libs = ['libjpeg-dev', 'libfreetype6-dev', 'zlib1g-dev', 'libpq-dev', ]
    requirements = packages + libs
    sudo('apt-get update -q')
    sudo('apt-get upgrade -yq')
    for lib in requirements:
        sudo('apt-get install -yq {0}'.format(lib))


@task
def setup_env():
    # Create user
    with settings(warn_only=True):
        result = sudo('id -u {0}'.format(config.user))
    if result.return_code == 1:
        sudo('adduser {0} --shell=/bin/false --group --system  --disabled-password --disabled-login'.format(config.user))

    # create folders
    mkdir(config.config_path)
    mkdir(config.log_path)
    mkdir(config.cache_path, group='www-data', mode=770)
    # no stat!
    sudo('mkdir --parents {0}'.format(config.share_path))


@task
def install_app():
    if exists(config.source_path):
        with cd(config.source_path):
            sudo('hg pull', user=config.user)
            sudo('hg up --clean {0}'.format(config.revision), user=config.user)
    else:
        cmd = 'hg clone --branch {0} https://bitbucket.org/b7w/bviewer {1}'
        sudo(cmd.format(config.revision, config.source_path), user=config.user)

    # Install app
    with pip_env():
        with cd(config.source_path):
            config_path = path.join(config.source_path, 'bviewer/settings/local.py')
            with hide('stdout'):
                sudo('python3 setup.py install --quiet')
            upload('app.conf.py', config_path)
            stat(config_path, mode=400)
            sudo('python3 manage.py syncdb --noinput', user=config.user)
            sudo('python3 manage.py collectstatic --noinput --verbosity=1', user=config.user)

    stat(path.join(config.source_path, 'static'), group='www-data')


@task
def setup_cron():
    crontab_path = path.join(config.config_path, 'crontab.txt')
    upload('crontab.txt', crontab_path)
    sudo('crontab {0}'.format(crontab_path), user=config.user)


@task
def install_redis():
    # sudo('add-apt-repository --yes ppa:rwky/redis')
    sudo('apt-get install -yq redis-server')


@task
def install_uwsgi():
    with pip_env():
        sudo('pip3 install --upgrade --quiet uwsgi')
        upload('uwsgi.init.conf', '/etc/init/uwsgi.conf')
        upload('uwsgi.ini', path.join(config.config_path, 'uwsgi.ini'))

    sudo('service uwsgi restart', warn_only=True)


@task
def install_nginx():
    sudo('apt-get install -yq nginx')
    upload('nginx.conf', '/etc/nginx/sites-enabled/bviewer.conf', backup=False)
    enabled = '/etc/nginx/sites-enabled/default'
    if exists(enabled):
        sudo('rm {0}'.format(enabled))
    sudo('service nginx restart')


@task
def deploy():
    setup_env()
    #install_libs()
    install_app()
    setup_cron()
    install_redis()
    install_uwsgi()
    install_nginx()


@task
def copy_resources():
    """
    Copy tests images
    """
    mkdir(config.share_path)
    put('resources', config.share_path, use_sudo=True)
    stat(config.share_path)
