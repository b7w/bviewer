# -*- coding: utf-8 -*-

import re
import time
from hashlib import sha1
from django.shortcuts import redirect
from django.utils.decorators import available_attrs

from django.utils.encoding import smart_str
from django.utils.functional import wraps

from bviewer.core import settings
from bviewer.core.models import ProxyUser

import logging

logger = logging.getLogger( __name__ )


class RaisingRange:
    """
    Iterator range that double sum base value if item/base == 8

    >>> RaisingRange(32, start=0, base=1)
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 16, 20, 24, 28]
    """

    def __init__(self, max, start=None, base=None):
        """
        max -> max value
        start -> start from or 0
        base -> base or 1
        """
        self.value = start or 0
        self.base = base or 1
        self.max = max

    def __iter__(self):
        return self

    def next(self):
        if self.value <= self.max:
            tmp = self.value
            if self.value / self.base == 8:
                self.base *= 2
            self.value += self.base
            return tmp
        else:
            raise StopIteration

    def __str__(self):
        return str( list( self ) )


class ResizeOptionsError( Exception ):
    """
    Resize options error.
    """
    pass


class ResizeOptions:
    """
    Options for resize such as width, height,
    max size - max of width/height,
    crop - need or not.
    """

    def __init__(self, size, user=None, storage=None, name=None):
        """
        Get sting with size "small" or "middle" or "big"
        storage -> path to the user storage,
        name -> file name,
        """
        self.user = user
        self.storage = storage
        self.name = name
        self.width = 0
        self.height = 0
        self.size = 0
        self.crop = False
        self.chooseSetting( size )

    def chooseSetting(self, size):
        if size == "small":
            self.setFromSetting( settings.VIEWER_SMALL_SIZE )
        elif size == "middle":
            self.setFromSetting( settings.VIEWER_MIDDLE_SIZE )
        elif size == "big":
            self.setFromSetting( settings.VIEWER_BIG_SIZE )
        elif size == "full":
            self.width = self.height = self.size = 10 ** 6
        else:
            raise ResizeOptionsError( "Undefined size format '{0}'".format( size ) )

    def setFromSetting(self, value):
        """
        Set values from settings.VIEWER_BIG_IMAGE for example
        """
        self.width = value['WIDTH']
        self.height = value['HEIGHT']
        self.size = max( self.width, self.height )
        self.crop = 'CROP' in value and value['CROP'] == True

    def __str__(self):
        return u"ResizeOptions{{user={us},storage={st},size={sz},crop={cr}}}"\
        .format( us=self.user, st=self.storage, sz=self.size, cr=self.crop )


class FileUniqueName:
    """
    Create unique hash name for file

        >>> builder = FileUnicName( )
        >>> time = builder.time()
        >>> time
        1323242186.620497
        >>> builder.build( "some/file", time=time )
        'fb41bb28d2614159246163f8dc77ac14'
        >>> builder.build( "some/file", time=builder.time() )
        '6ef61d7c41d391fcd17dd59e1d29dfc2'
        >>> builder.build( "some/file", time=time, extra='tag1' )
        'bb89a8697e7f2acfd5d904bc96ce5b81'
    """

    def __init__(self ):
        pass

    def hash(self, name):
        """
        Return md5 of "files.storage" + name
        """
        return sha1( "files.storage" + smart_str( name ) ).hexdigest( )

    def time(self):
        """
        Return just time.time( )
        """
        return time.time( )

    def build(self, path, time=None, extra=None):
        """
        return unic name of path + [extra]
        """
        full_name = settings.VIEWER_CACHE_PATH + path
        if time:
            if time == True:
                full_name += str( self.time( ) )
            else:
                full_name += str( time )
        if extra:
            full_name += str( extra )
        return self.hash( full_name )


domain_match = re.compile( "([w]{3})?\.?(?P<sub>\w+)\.(\w+)\.([a-z]+):?(\d{0,4})" )

def get_gallery_user( request, name=None ):
    """
    Detect gallery user. first try to get from [www.]{username}.domain.com[:port], than /{username}/..., and get auth user.
    If nothing return ( None, '' ). first is user, second is user url.

    :type request: django.http.HttpRequest
    :type name: string
    :rtype: (bviewer.core.models.ProxyUser, string)
    """
    match = domain_match.match( request.get_host( ) )
    if match:
        name = match.group( 'sub' )
        user = ProxyUser.objects.safe_get( url=name )
        if user:
            return user, ''
    elif name:
        user = ProxyUser.objects.safe_get( url=name )
        if user:
            return user, name + '/'
    elif request.user.is_authenticated( ):
        user = ProxyUser.objects.get( id=request.user.id )
        return user, user.username.lower( ) + '/'
    return None, ''


def perm_any_required( *args, **kwargs):
    """
    Decorator for views that checks if at least one permission return True,
    redirecting to the `url` page on False.
    """
    url = kwargs.get( "url", '/' )

    def test_func( user ):
        for perm in args:
            if user.has_perm( perm ):
                return True

    def decorator(view_func):
        @wraps( view_func, assigned=available_attrs( view_func ) )
        def _wrapped_view(request, *args, **kwargs):
            if test_func( request.user ):
                return view_func( request, *args, **kwargs )
            return redirect( url )

        return _wrapped_view

    return decorator