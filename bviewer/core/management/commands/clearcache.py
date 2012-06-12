# -*- coding: utf-8 -*-


import os
from operator import itemgetter
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.core.management.color import no_style

from bviewer.core import settings
from bviewer.core.models import ProxyUser

import logging

logger = logging.getLogger(__name__)


def multi_sort(items, columns):
    """
    Multi key sort. Get list of `columns` in str, with '-{key}' as reverse.

        >>> multi_sort(files, columns=('-size', 'time'))

    :type items: list
    :type columns: tuple
    :rtype: list
    """
    compares = [((itemgetter(col[1:].strip()), -1) if col.startswith('-') else (itemgetter(col.strip()), 1)) for col in columns]

    def compare(left, right):
        for fn, multi, in compares:
            result = cmp(fn(left), fn(right))
            if result:
                return multi * result
        else:
            return 0

    return sorted(items, cmp=compare)


class ClearCache(object):
    """
    Delete old files in cache directory. First big size.
    So all zip archive will be deleted first by schedule, if no user space available
    """
    def __init__(self, path, size=None, time=None):
        self.max_size = size or 32
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
        profile = ProxyUser.objects.safe_get(url=user)
        if profile:
            size = profile.cache_size * 2 ** 20
        else:
            size = self.max_size
        files = multi_sort(files, columns=('size', 'time'))
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