# -*- coding: utf-8 -*-

import os
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.core.management.color import no_style

from core import settings
from core.models import ProxyUser

import logging

logger = logging.getLogger( __name__ )


class ClearCache( object ):
    def __init__(self, path, size=None, time=None):
        self.max_size = size
        self.older = time or 7 * 24 * 60 * 60
        self.cache_path = path

    def clear(self):
        logger.info( "Start clearing cache" )
        for user in os.listdir( self.cache_path ):
            logger.debug( "Start clearing %s user cache", user )
            user_full = os.path.join( self.cache_path, user )
            data = []
            for item in os.listdir( user_full ):
                file = os.path.join( user_full, item )
                if os.path.islink( file ):
                    self.clear_time( file, user )
                else:
                    i = {"path": file, "size": self.getsize( file ), "time": self.getctime( file )}
                    data.append( i )
            self.clear_size( data, user )

    def clear_time(self, path, user ):
        created = self.getctime( path )
        if datetime.now( ) - created > timedelta( seconds=self.older ):
            os.remove( path )
            logger.info( "clear %s user '%s' link", user, path )

    def clear_size(self, files, user):
        profile = ProxyUser.objects.get( url=user )
        if not self.max_size:
            size = profile.cache_size * 2 ** 20
        else:
            size = self.max_size
        files = sorted( files, key=lambda f: f["time"] )
        flag = True
        while flag:
            s = sum( i["size"] for i in files )
            if s > size:
                file = files.pop( )
                os.remove( file["path"] )
                logger.info( "clear %s user '%s' cache", user, file["path"] )
            else:
                flag = False

    def getctime(self, path):
        return datetime.fromtimestamp( os.path.getctime( path ) )

    def getsize(self, path):
        return os.path.getsize( path )


class Command( BaseCommand ):
    args = u"[size in MB]"
    help = u"Clear old links and delete old files if size of user cache is bigger or given"

    def handle(self, *args, **options):
        self.style = no_style( )
        if not len( args ):
            cache = ClearCache( path=settings.VIEWER_CACHE_PATH )
        else:
            size = int( args[0] ) * 2 ** 20
            cache = ClearCache( path=settings.VIEWER_CACHE_PATH, size=size )
        cache.clear( )