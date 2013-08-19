# -*- coding: utf-8 -*-
#
# Simple fab file to help start, run and test application
#
from fabric.api import run
from fabric.context_managers import cd, hide
from fabric.operations import sudo
from fabric.utils import puts


__all__ = ['test', 'clear', 'static', 'update', ]


def test(path, user='believe'):
    """
    Runs app tests, just a proxy command
    """
    puts('Runs app tests')
    with cd(path):
        puts('Core module tests ')
        sudo('python manage.py test core --settings=bviewer.settings.test', user=user)
        puts('API module tests ')
        sudo('python manage.py test api --settings=bviewer.settings.test', user=user)
        puts('Archive module tests ')
        sudo('python manage.py test archive --settings=bviewer.settings.test', user=user)


def clear(path):
    """
    Delete cache, just a proxy command
    """
    puts('Delete all cache')
    with cd(path):
        puts('Core module tests ')
        sudo('rm -rf cache')
        sudo('rm -rf tests')


def static(path, user='believe'):
    """
    Collect and gzip static files.
    """
    puts('Collect and gzip static files')
    with cd(path):
        sudo('python manage.py collectstatic --noinput', user=user)

        with hide('running', 'stdout'):
            puts('run: gzip -6 -c ...')

            paths = sudo('find static -name "*.js" -type f')
            for js_path in paths.split():
                sudo('gzip -6 -c {0} > {0}.gz'.format(js_path), user=user)
            paths = run('find static -name "*.css" -type f')
            for css_path in paths.split():
                sudo('gzip -6 -c {0} > {0}.gz'.format(css_path), user=user)

            sudo('find static -type f -exec chmod 644 {} \;', user=user)


def update(path, rev='default', user='believe'):
    """
    Update hg to rev='default'
    """
    puts('Update hg to revision {0}'.format(rev))
    with cd(path):
        sudo('hg pull', user=user)
        sudo('hg update -r {0}'.format(rev), user=user)

    static(path, user=user)
    sudo('service uwsgi restart')