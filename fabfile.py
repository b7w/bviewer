# -*- coding: utf-8 -*-

import os, sys
from pwd import getpwnam
import shutil

from fabric.context_managers import cd
from fabric.operations import local

from src import settings

__all__ = ['help', 'start', 'stop', 'syncdb', 'clear', 'static']

HOME = settings.SOURCE_PATH

NAME = getattr( settings, 'NAME', 'believe' )
PID = getattr( settings, 'PID', '/var/run/limited' )
NICE = getattr( settings, 'NICE', 0 )
USER = getattr( settings, 'USER', 'www-data' )
GROUP = getattr( settings, 'GROUP', 'www-data' )

MANAGE_PY = os.path.join( getattr( settings, 'SOURCE_PATH' ), 'manage.py' )
CELERY_ARGS = getattr( settings, 'CELERY_ARGS', '-B' )

CELERY_START = """start-stop-daemon --start --quiet --oknodo --background --make-pidfile \
 --chdir {home} --name {name} --pidfile {pid} --nicelevel {nice} --chuid {user} \
 --exec {daemon} -- {options}"""

CELERY_STOP = """start-stop-daemon --stop --pidfile {pid}"""

def get_pid(name):
    """
    Get pid path /var/run + NAME.lower() + name
    """
    dir = os.path.join( '/var/run', NAME.lower( ) )
    if not os.path.exists( dir ):
        os.mkdir( dir )
    os.chown( dir, getpwnam( USER ).pw_uid, getpwnam( GROUP ).pw_gid )
    file = os.path.join( dir, name )
    return file


def list_files( path, ends=None ):
    """
    Return list with full path paths to all files under ``path`` directory.
    if ``ends`` contains list of file extensions only this files will be included.
    """

    def _list_files( path, array):
        for name in os.listdir( path ):
            full_path = os.path.join( path, name )
            if os.path.isdir( full_path ):
                array = _list_files( full_path, array )
            if os.path.isfile( full_path ):
                if ends is not None:
                    for ext in ends:
                        if full_path.endswith( '.' + ext ):
                            array.append( full_path )
        return array

    return _list_files( path, [] )


def start():
    """
    Start celery daemon from manage.py with default django settings file.
    djcelery should be installed, but can not be in install apps.
    settings: NICE=0, USER=www-data, GROUP=www-data, CELERY_ARGS=-B
    """
    args = {
        'home': HOME,
        'name': NAME,
        'nice': NICE,
        'pid': get_pid( 'celery.pid' ),
        'user': USER,
        'daemon': MANAGE_PY,
        'options': 'celeryd ' + CELERY_ARGS,
        }
    with cd( HOME ):
        local( CELERY_START.format( **args ) )


def stop():
    """
    Stop celery daemon
    """
    print( "[ INFO ] Start celery" )
    args = {
        'pid': get_pid( 'celery.pid' ),
        }
    local( CELERY_STOP.format( **args ) )


def syncdb():
    """
    Sync database, just a proxy command
    """
    print( "[ INFO ] Sync database" )
    local( '{0} syncdb'.format( MANAGE_PY ) )


def clear():
    """
    Delete cache, just a proxy command
    """
    print( "[ INFO ] Delete all cache" )
    for item in os.listdir( settings.VIEWER_CACHE_PATH ):
        shutil.rmtree( os.path.join( settings.VIEWER_CACHE_PATH, item ) )


def static():
    """
    Collect and gzip static files.
    Delete previous folder.
    """

    print( "[ INFO ] Collect and gzip static " )
    if os.path.exists( settings.STATIC_ROOT ):
        shutil.rmtree( settings.STATIC_ROOT )
    local( "python {manage} collectstatic --noinput".format( manage=MANAGE_PY ) )

    files = list_files( settings.STATIC_ROOT, ("css", "js",) )
    for item in files:
        os.system( "gzip -6 -c {0} > {0}.gz".format( item ) )
    local( "find {0} -type f -exec chmod {1} {{}} \;".format( settings.STATIC_ROOT, 644 ) )


def help():
    """
    Print help for commands
    """
    print( "It is a small helper to install and run LimitedFM" )
    print( "Usage: fab command[:arg,arg2] command .." )
    print( "" )
    module = sys.modules[__name__]
    for item in __all__:
        attr = module.__dict__[item]
        print( "{name} {doc}".format( name=item, doc=attr.__doc__ ) )