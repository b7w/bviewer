# -*- coding: utf-8 -*-
#
# Simple fab file to help start, run and test application
#
import os
import sys
import shutil

from bviewer import settings


__all__ = ['syncdb', 'test', 'clear', 'static']

MANAGE_PY = os.path.join(getattr(settings, 'PROJECT_PATH'), 'manage.py')


def list_files(path, ends=None):
    """
    Return list with full path paths to all files under ``path`` directory.
    if ``ends`` contains list of file extensions only this files will be included.
    """

    def _list_files(path, array):
        for name in os.listdir(path):
            full_path = os.path.join(path, name)
            if os.path.isdir(full_path):
                array = _list_files(full_path, array)
            if os.path.isfile(full_path):
                if ends is not None:
                    for ext in ends:
                        if full_path.endswith('.' + ext):
                            array.append(full_path)
        return array

    return _list_files(path, [])


def syncdb():
    """
    Sync database, just a proxy command
    """
    print('[ INFO ] Sync database')
    os.system('python {0} -- syncdb'.format(MANAGE_PY))


def test():
    """
    Runs app tests, just a proxy command
    """
    print('[ INFO ] Run core module tests ')
    os.system('python {0} test core --settings=bviewer.settings.test'.format(MANAGE_PY))
    print('[ INFO ] Run api module tests ')
    os.system('python {0} test api --settings=bviewer.settings.test'.format(MANAGE_PY))


def clear():
    """
    Delete cache, just a proxy command
    """
    print('[ INFO ] Delete all cache')
    for item in os.listdir(settings.VIEWER_CACHE_PATH):
        shutil.rmtree(os.path.join(settings.VIEWER_CACHE_PATH, item))


def static():
    """
    Collect and gzip static files.
    """

    print('[ INFO ] Collect and gzip static')
    os.system('python {manage} collectstatic --noinput'.format(manage=MANAGE_PY))

    files = list_files(settings.STATIC_ROOT, ('css', 'js',))
    for item in files:
        os.system('gzip -6 -c {0} > {0}.gz'.format(item))
    os.system('find {0} -type f -exec chmod {1} {{}} \;'.format(settings.STATIC_ROOT, 644))


def help():
    """
    Print help for commands
    """
    print('Usage: fab command[:arg,arg2] command ..')
    print('')
    module = sys.modules[__name__]
    for item in __all__:
        attr = module.__dict__[item]
        print( '{name} {doc}'.format(name=item, doc=attr.__doc__) )