# -*- coding: utf-8 -*-
import json
from os import path
import time

from fabric.main import main
from fabric.utils import abort
from fabric.state import env
from fabric.colors import green
from fabric.decorators import task
from fabric.context_managers import cd, settings, hide, shell_env
from fabric.contrib.files import exists, upload_template
from fabric.operations import sudo, put


if __name__ == '__main__':
    main()


def load_config():
    class Config(dict):
        __getattr__ = dict.__getitem__

    conf = Config(
        domains=NotImplemented,
        proxy=NotImplemented,
        shares=[],
        revision='default',
        user='bviewer',
        python_version='3.4.2',
        server_email='noreply@bviewer.loc',
        python_home='/home/bviewer/python',
        source_path='/home/bviewer/source',
        source_clone=True,  # clone form scr or copy from local folder
        config_path='/home/bviewer/configs',
        log_path='/home/bviewer/logs',
        run_path='/var/run/bviewer',
        cache_path='/home/bviewer/cache',
        share_path='/home/bviewer/share',
    )
    if 'env' not in env:
        abort('No env setup, add --set env=dev')
    conf['python_path'] = path.join(conf.python_home, conf.python_version, 'bin')
    with open(path.join('configs', env.env, 'deploy.json')) as f:
        result = json.load(f)
        conf.update(result)
    return conf


config = load_config()


# Helpers
def upload(filename, destination, **kwargs):
    context = dict(kwargs.pop('context', {}), **config)
    override = path.join('configs', env.env, filename)
    if path.exists(override):
        source = override
    else:
        source = path.join('configs', filename)
    upload_template(source, destination, context=context, use_jinja=True, use_sudo=True, backup=False, **kwargs)


def echo(msg):
    print(green(msg))


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
    echo('# Install packages and libs')
    requirements = 'software-properties-common python-software-properties build-essential ' \
                   'cifs-utils htop mercurial git ' \
                   'libsqlite3-dev sqlite3 bzip2 libbz2-dev ' \
                   'libjpeg-dev libfreetype6-dev zlib1g-dev libpq-dev'
    with hide('stdout'):
        sudo('apt-get update -q')
    # sudo('apt-get upgrade -yq')
    sudo('apt-get install -yq {0}'.format(requirements))


@task
def setup_env():
    echo('# Setup environment')
    # Create user
    with settings(warn_only=True):
        result = sudo('id -u {0}'.format(config.user))
    if result.return_code == 1:
        sudo(
            'adduser {0} --shell=/bin/false --group --system  --disabled-password --disabled-login'.format(config.user))

    # create folders
    mkdir(config.config_path, user='root', group='root')
    mkdir(config.log_path)
    mkdir(config.cache_path, group='www-data', mode=770)


@task
def install_python():
    echo('# Install python')
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
    echo('# Install application')
    if config.source_clone:
        if exists(config.source_path):
            with cd(config.source_path):
                sudo('hg pull', user=config.user)
                sudo('hg up --clean {0}'.format(config.revision), user=config.user)
        else:
            cmd = 'hg clone --branch {0} https://bitbucket.org/b7w/bviewer {1}'
            sudo(cmd.format(config.revision, config.source_path), user=config.user)
    else:
        sudo('rm -rf {0}'.format(config.source_path))
        mkdir(config.source_path)
        sudo('cp -r /provision/* {0}'.format(config.source_path))
        stat(config.source_path)

    # Install app
    with pip_env():
        with cd(config.source_path):
            config_path = path.join(config.source_path, 'bviewer/settings/local.py')
            with hide('stdout'):
                pip('install --upgrade --editable .')
            upload('app.conf.py', config_path)
            stat(config_path, mode=400)
            python('manage.py migrate --noinput', user=config.user)
            python('manage.py collectstatic --noinput --verbosity=1', user=config.user)

    static_path = path.join(config.source_path, 'static')
    stat(static_path, group='www-data')


@task
def setup_cron():
    echo('# Setup cron')
    crontab_path = path.join(config.config_path, 'crontab.txt')
    upload('crontab.txt', crontab_path)
    sudo('crontab {0}'.format(crontab_path), user=config.user)


@task
def mount_shares():
    echo('# Mount shares')
    # May required for virtual machines
    # sudo('apt-get install -yq linux-image-extra-virtual')
    uid = sudo('id -u {0}'.format(config.user))
    gid = sudo('id -u {0}'.format('www-data'))
    # no stat!
    sudo('mkdir --parents {0}'.format(config.share_path))
    for item in config.shares:
        item['to'] = item['to'].format(**config)
        item['options'] = item['options'] + ',uid={0},gid={1}'.format(uid, gid)
    upload('share.init.conf', '/etc/init/share.conf')
    result = sudo('service share restart', warn_only=True)
    if 'failed' in result:
        abort(result)


@task
def install_redis():
    echo('# Install redis')
    sudo('apt-get install -yq redis-server')


@task
def install_uwsgi():
    echo('# Install uwsgi')
    with pip_env():
        pip('install --upgrade --quiet uwsgi')
        upload('uwsgi.init.conf', '/etc/init/uwsgi.conf')
        upload('uwsgi.ini', path.join(config.config_path, 'uwsgi.ini'))

    sudo('service uwsgi restart')


@task
def install_nginx():
    echo('# Install nginx')
    with hide('stdout'):
        sudo('add-apt-repository --yes ppa:nginx/stable')
        sudo('apt-get update -q')
    sudo('apt-get install -yq nginx')
    upload('nginx.conf', '/etc/nginx/sites-enabled/bviewer.conf')
    certificate_crt = path.join(config.config_path, 'nginx.ssl.crt')
    certificate_key = path.join(config.config_path, 'nginx.ssl.key')
    upload('nginx.ssl.crt', certificate_crt)
    upload('nginx.ssl.key', certificate_key)
    stat(certificate_crt, user='root', group='root', mode=640)
    stat(certificate_key, user='root', group='root', mode=640)
    enabled = '/etc/nginx/sites-enabled/default'
    if exists(enabled):
        sudo('rm {0}'.format(enabled))
    sudo('service nginx restart')


@task
def deploy():
    """
    Make full setup on new OS or safely update app
    """
    t1 = time.time()
    echo('## Deploy')
    setup_env()
    install_libs()
    install_python()
    install_redis()
    install_app()
    install_uwsgi()
    install_nginx()
    setup_cron()
    mount_shares()
    t2 = int(time.time() - t1)
    print('## Complete, {0:d} min and {1:d} sec'.format(t2 // 60, t2 % 60))


@task
def deploy_proxy():
    """
    Deploy nginx proxy config with ssl and 502.html
    Ensure nginx installed.
    Take two strings public domains for server_name and privet_domain for proxy pass
    """
    echo('# Deploy proxy')
    public_domains = config.proxy['from']
    privet_domain = config.proxy['to']

    certificate_crt = '/etc/nginx/ssl/bviewer.crt'
    certificate_key = '/etc/nginx/ssl/bviewer.key'

    mkdir('/etc/nginx/ssl', user='root', group='root')
    upload('nginx.ssl.crt', certificate_crt)
    upload('nginx.ssl.key', certificate_key)
    stat(certificate_crt, user='root', group='root')
    stat(certificate_key, user='root', group='root')

    mkdir('/etc/nginx/html/bviewer', user='root', group='www-data')
    put('bviewer/templates/502.html', '/etc/nginx/html/bviewer/502.html', use_sudo=True)
    stat('/etc/nginx/html', user='root', group='www-data', mode=644)

    nginx_conf = '/etc/nginx/sites-enabled/proxy.bviewer.conf'
    context = dict(public_domains=public_domains, privet_domain=privet_domain)
    upload('nginx.proxy.conf', nginx_conf, context=context)
    stat(nginx_conf, user='root', group='root')
    sudo('service nginx reload')


@task
def deploy_vagrant():
    """
    Deploy and load data for vagrant demo installation
    """
    deploy()
    with pip_env():
        with cd(config.source_path):
            python('manage.py initdemo', user=config.user)


@task
def copy_resources():
    """
    Copy tests images
    """
    echo('# Copy resources')
    mkdir(config.share_path)
    put('resources', config.share_path, use_sudo=True)
    stat(config.share_path)
