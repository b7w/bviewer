# -*- coding: utf-8 -*-
from fabric.colors import green
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
        domains=NotImplemented,
        shares=[],
        revision='default',
        user='bviewer',
        python_version='3.4.1',
        python_home='/home/bviewer/python',
        source_path='/home/bviewer/source',
        config_path='/home/bviewer/configs',
        log_path='/home/bviewer/logs',
        run_path='/var/run/bviewer',
        cache_path='/home/bviewer/cache',
        share_path='/home/bviewer/share',
    )
    conf['python_path'] = path.join(conf.python_home, conf.python_version, 'bin')
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


def python(cmd, **kwargs):
    binary = path.join(config.python_path, 'python3')
    return sudo('{} {}'.format(binary, cmd), **kwargs)


def pip(cmd, **kwargs):
    binary = path.join(config.python_path, 'pip3')
    return sudo('{} {}'.format(binary, cmd), **kwargs)


# Tasks
@task
def install_libs():
    print(green('# Install packages and libs'))
    requirements = 'build-essential cifs-utils htop mercurial git ' \
                   'libsqlite3-dev sqlite3 bzip2 libbz2-dev ' \
                   'libjpeg-dev libfreetype6-dev zlib1g-dev libpq-dev'
    with hide('stdout'):
        sudo('apt-get update -q')
    sudo('apt-get upgrade -yq')
    sudo('apt-get install -yq {0}'.format(requirements))


@task
def setup_env():
    print(green('# Setup environment'))
    # Create user
    with settings(warn_only=True):
        result = sudo('id -u {0}'.format(config.user))
    if result.return_code == 1:
        sudo('adduser {0} --shell=/bin/false --group --system  --disabled-password --disabled-login'.format(config.user))

    # create folders
    mkdir(config.config_path)
    mkdir(config.log_path)
    mkdir(config.cache_path, group='www-data', mode=770)


@task
def install_python():
    print(green('# Install python'))
    ver = config.python_version
    ver_path = path.join(config.python_home, ver)
    arch_path = path.join(config.python_home, 'Python-{0}.tar.xz'.format(ver))
    mkdir(config.python_home)
    if not exists(ver_path) or exists(arch_path):
        with cd(config.python_home):
            sudo('wget --no-verbose https://www.python.org/ftp/python/{0}/Python-{0}.tar.xz'.format(ver))
            with hide('stdout'):
                sudo('tar xJf Python-{0}.tar.xz'.format(ver))
                with cd(path.join(config.python_home, 'Python-{0}'.format(ver))):
                    sudo('./configure --prefix={0}'.format(ver_path))
                    sudo('make && sudo make install')
            sudo('rm -rf Python-{0}'.format(ver))
            sudo('rm -rf Python-{0}.tar.xz'.format(ver))


@task
def install_app():
    print(green('# Install application'))
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
                python('setup.py install --quiet')
            upload('app.conf.py', config_path)
            stat(config_path, mode=400)
            python('manage.py syncdb --noinput', user=config.user)
            python('manage.py collectstatic --noinput --verbosity=1', user=config.user)

    stat(path.join(config.source_path, 'static'), group='www-data')


@task
def setup_cron():
    print(green('# Setup cron'))
    crontab_path = path.join(config.config_path, 'crontab.txt')
    upload('crontab.txt', crontab_path)
    sudo('crontab {0}'.format(crontab_path), user=config.user)


@task
def mount_shares():
    print(green('# Mount shares'))
    uid = sudo('id -u {0}'.format(config.user))
    gid = sudo('id -u {0}'.format('www-data'))
    # no stat!
    sudo('mkdir --parents {0}'.format(config.share_path))
    for item in config.shares:
        # item['from'] = item['from'].replace(' ', '\\040')
        item['to'] = item['to'].format(**config)
        item['options'] = item['options'] + ',uid={0},uid={1}'.format(uid, gid)
    upload('share.init.conf', '/etc/init/share.conf')
    sudo('service share start', warn_only=True)


@task
def install_redis():
    print(green('# Install redis'))
    # sudo('add-apt-repository --yes ppa:rwky/redis')
    sudo('apt-get install -yq redis-server')


@task
def install_uwsgi():
    print(green('# Install uwsgi'))
    with pip_env():
        pip('install --upgrade --quiet uwsgi')
        upload('uwsgi.init.conf', '/etc/init/uwsgi.conf')
        upload('uwsgi.ini', path.join(config.config_path, 'uwsgi.ini'))

    sudo('service uwsgi restart', warn_only=True)


@task
def install_nginx():
    print(green('# Install nginx'))
    sudo('apt-get install -yq nginx')
    upload('nginx.conf', '/etc/nginx/sites-enabled/bviewer.conf', backup=False)
    certificate_crt = path.join(config.config_path, 'nginx.ssl.crt')
    certificate_key = path.join(config.config_path, 'nginx.ssl.key')
    upload('nginx.ssl.crt', certificate_crt, backup=False)
    upload('nginx.ssl.key', certificate_key, backup=False)
    stat(certificate_crt, user='root', mode=440)
    stat(certificate_key, user='root', mode=440)
    enabled = '/etc/nginx/sites-enabled/default'
    if exists(enabled):
        sudo('rm {0}'.format(enabled))
    sudo('service nginx restart')


@task
def deploy():
    print(green('## Deploy'))
    setup_env()
    install_libs()
    install_python()
    install_app()
    setup_cron()
    mount_shares()
    install_redis()
    install_uwsgi()
    install_nginx()


@task
def copy_resources():
    """
    Copy tests images
    """
    print(green('# Copy resources'))
    mkdir(config.share_path)
    put('resources', config.share_path, use_sudo=True)
    stat(config.share_path)
