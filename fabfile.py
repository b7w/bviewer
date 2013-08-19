# -*- coding: utf-8 -*-
#
# Simple fab file to help start, run and test application
#

from fabric.api import run
from fabric.context_managers import cd, hide
from fabric.utils import puts


__all__ = ['test', 'clear', 'static']


def test(path):
    """
    Runs app tests, just a proxy command
    """
    puts('Runs app tests')
    with cd(path):
        puts('Core module tests ')
        run('python manage.py test core --settings=bviewer.settings.test')
        puts('API module tests ')
        run('python manage.py test api --settings=bviewer.settings.test')
        puts('Archive module tests ')
        run('python manage.py test archive --settings=bviewer.settings.test')


def clear(path):
    """
    Delete cache, just a proxy command
    """
    puts('Delete all cache')
    with cd(path):
        puts('Core module tests ')
        run('rm -rf cache')
        run('rm -rf tests')


def static(path):
    """
    Collect and gzip static files.
    """
    puts('Collect and gzip static files')
    with cd(path):
        run('python manage.py collectstatic --noinput')

        with hide('running', 'stdout'):
            puts('run: gzip -6 -c ...')

            paths = run('find static -name "*.js" -type f')
            for js_path in paths.split():
                run('gzip -6 -c {0} > {0}.gz'.format(js_path))
            paths = run('find static -name "*.css" -type f')
            for css_path in paths.split():
                run('gzip -6 -c {0} > {0}.gz'.format(css_path))

            run('find static -type f -exec chmod 644 {} \;')