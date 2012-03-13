# -*- coding: utf-8 -*-

import os, sys
from pwd import getpwnam
import shutil

from fabric.context_managers import cd

from src import settings

__all__ = ["help", "start", "stop", "restart", "syncdb", "clear", "static"]

HOME = settings.SOURCE_PATH

NAME = getattr( settings, "NAME", "believe" )
USER = getattr( settings, "USER", "www-data" )
GROUP = getattr( settings, "GROUP", "www-data" )

MANAGE_PY = os.path.join( getattr( settings, "SOURCE_PATH" ), "manage.py" )
RUN_DIR = os.path.join( "/var/run", NAME.lower( ) )

CELERY_ARGS = getattr( settings, "CELERY_ARGS", "-B" )
CELERY_NICE = getattr( settings, "CELERY_NICE", 0 )
DJANGO_ARGS = getattr( settings, "DJANGO_ARGS", "maxspare=4 maxchildren=8" )

CELERY_START = """start-stop-daemon --start --quiet --oknodo --background --make-pidfile \
 --chdir {home} --name {name} --pidfile {pid} --nicelevel {nice} --chuid {user} \
 --exec {daemon} -- {options}"""

DJANGO_START = """su {user} -c "python {manage} runfcgi socket={sock} pidfile={pid} {args}" """


def get_pid(name):
    """
    Get pid path /var/run + NAME.lower() + name
    """
    if not os.path.exists( RUN_DIR ):
        os.mkdir( RUN_DIR )
    file = os.path.join( RUN_DIR, name )
    return file


def chmod():
    """
    Chown run directory
    """
    for file in os.listdir( RUN_DIR ):
        path = os.path.join( RUN_DIR, file )
        os.chown( path, getpwnam( USER ).pw_uid, getpwnam( GROUP ).pw_gid )
        os.chmod( path, int( "775", 8 ) )


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
                        if full_path.endswith( "." + ext ):
                            array.append( full_path )
        return array

    return _list_files( path, [] )


def start():
    """
    Start celery and django daemon from manage.py with default django settings file.
    djcelery should be installed, but can not be in install apps.
    settings: CELERY_NICE=0, USER=www-data, GROUP=www-data, CELERY_ARGS=-B
    """
    if os.getuid( ):
        print("Only root can run program from another user")
    else:
        celery_args = {
            "home": HOME,
            "name": NAME,
            "nice": CELERY_NICE,
            "pid": get_pid( "celery.pid" ),
            "user": USER,
            "daemon": MANAGE_PY,
            "options": "celeryd " + CELERY_ARGS,
            }
        django_args = {
            "manage": MANAGE_PY,
            "user": USER,
            "pid": get_pid( "django.pid" ),
            "sock": get_pid( "django.sock" ),
            "args": DJANGO_ARGS,
            }
        with cd( HOME ):
            print( "[ INFO ] Start celery" )
            os.system( CELERY_START.format( **celery_args ) )
            print( "[ INFO ] Start django" )
            os.system( DJANGO_START.format( **django_args ) )
        chmod( )


def stop():
    """
    Stop celery and django daemon
    """
    if os.getuid( ):
        print("Only root can stop program of another user")
    else:
        print( "[ INFO ] Stop celery" )
        os.system( "kill `cat {pid}`".format( pid=get_pid( "celery.pid" ) ) )
        print( "[ INFO ] Stop django" )
        os.system( "kill `cat {pid}`".format( pid=get_pid( "django.pid" ) ) )


def restart():
    """
    Restart celery and django
    """
    if os.getuid( ):
        print("Only root can restart program of another user")
    else:
        stop( )
        start( )


def syncdb():
    """
    Sync database, just a proxy command
    """
    print( "[ INFO ] Sync database" )
    os.system( "python {0} syncdb".format( MANAGE_PY ) )


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

    print( "[ INFO ] Collect and gzip static" )
    if os.path.exists( settings.STATIC_ROOT ):
        shutil.rmtree( settings.STATIC_ROOT )
    os.system( "python {manage} collectstatic --noinput".format( manage=MANAGE_PY ) )

    files = list_files( settings.STATIC_ROOT, ("css", "js",) )
    for item in files:
        os.system( "gzip -6 -c {0} > {0}.gz".format( item ) )
    os.system( "find {0} -type f -exec chmod {1} {{}} \;".format( settings.STATIC_ROOT, 644 ) )


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