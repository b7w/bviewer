# -*- coding: utf-8 -*-

import os
import re
import time
from PIL import Image
from hashlib import sha1
import urllib2
import cStringIO
from django.shortcuts import redirect
from django.utils.decorators import available_attrs

from django.utils.encoding import smart_str
from django.utils.functional import wraps

from core import settings
from core.models import ProxyUser

import logging

logger = logging.getLogger( __name__ )


class ResizeImage( object ):
    """
    Get file with image. Resize, crop it.
    """

    def __init__(self, filein):
        self.file = Image.open( filein )
        if self.file.mode not in ('L', 'RGB'):
            self.file = self.file.convert( 'RGB' )
        self.quality = 95
        self.type = "JPEG"

    @property
    def width(self):
        """
        Return image width
        """
        return self.file.size[0]

    @property
    def height(self):
        """
        Return image height
        """
        return self.file.size[1]

    def resize(self, width, height):
        """
        Resize image to ``width`` and ``width``
        """
        self.file = self.file.resize( (width, height), Image.ANTIALIAS )

    def crop(self, x_offset, y_offset, width, height ):
        """
        Crop image with ``x_offset``, ``y_offset``, ``width``, ``height``
        """
        self.file = self.file.crop( (x_offset, y_offset, width, height) )

    def cropCenter(self, width, height):
        """
        Cut out an image with ``width`` and ``height`` of the center
        """
        x_offset = ( self.width - width ) / 2
        y_offset = ( self.height - height ) / 2
        self.crop( x_offset, y_offset, x_offset + width, y_offset + height )

    def isPortrait(self):
        """
        Is width < height
        """
        return self.width < self.height

    def isLandscape(self):
        """
        Is width >= height
        """
        return self.width >= self.height

    def isBigger(self, width, height):
        """
        Is this image bigger that ``width`` and ``height``
        """
        return self.width > width  and self.height > height

    def minSize(self, value):
        """
        Scale images size where the min size len will be ``value``
        """
        if self.isLandscape( ):
            scale = float( self.height ) / value
            width = int( self.width / scale )
            return width, value
        else:
            scale = float( self.width ) / value
            height = int( self.height / scale )
            return value, height

    def maxSize(self, value):
        """
        Scale images size where the max size len will be ``value``
        """
        if self.isPortrait( ):
            scale = float( self.height ) / value
            width = int( self.width / scale )
            return width, value
        else:
            scale = float( self.width ) / value
            height = int( self.height / scale )
            return value, height

    def saveTo(self, fileio ):
        """
        Save to open file ``fileio``. Need to close by yourself.
        """
        self.file.save( fileio, self.type, quality=self.quality )


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
        return "ResizeOptions{{user={us},storage={st},size={sz},crop={cr}}}"\
        .format( us=self.user, st=self.storage, sz=self.size, cr=self.crop )


class CacheImage( object ):
    """
    It is a facade for Resize image that resize images and cache it in `settings.VIEWER_CACHE_PATH`
    """

    def __init__(self, path, options ):
        """
        path -> path to image,
        options -> ResizeOptions
        """
        self.path = path
        self.options = options
        # each user will have his own cache dir
        self.cache_dir = os.path.join( settings.VIEWER_CACHE_PATH, options.user )

        self.hash = self.get_hash_name( )
        self.url = os.path.join( options.user, self.hash + ".jpg" )
        self.cache = os.path.join( self.cache_dir, self.hash + ".jpg" )

    def get_hash_name(self):
        self.hash_builder = FileUniqueName( )
        if self.options.name:
            return self.hash_builder.build( self.options.name, extra=self.options.size )
        return self.hash_builder.build( self.path, extra=self.options.size )


    def process(self):
        """
        Get image from storage and save it to cache. If image is to big, resize. If to small, link.
        If cache already exists, do nothing
        """
        self.checkCacheDir( )
        abs_path = os.path.join( settings.VIEWER_STORAGE_PATH, self.options.storage, self.path )
        if not os.path.lexists( self.cache ):
            with open( abs_path, mode='rb' ) as filein:
                newImage = ResizeImage( filein )
                bigger = newImage.isBigger( self.options.width, self.options.height )
                if bigger:
                    if self.options.crop:
                        w, h = newImage.minSize( self.options.size )
                        newImage.resize( w, h )
                        newImage.cropCenter( self.options.width, self.options.height )
                    else:
                        w, h = newImage.maxSize( self.options.size )
                        newImage.resize( w, h )
                    with open( self.cache, mode='wb' ) as fileout:
                        newImage.saveTo( fileout )
                else:
                    os.symlink( abs_path, self.cache )

    def download(self):
        """
        Download image and put to cache.
        If cache exists, do nothing
        """
        self.checkCacheDir( )
        if not os.path.exists( self.cache ):
            image = cStringIO.StringIO( )
            image.write( urllib2.urlopen( self.path ).read( ) )
            image.seek( 0 )
            newImage = ResizeImage( image )
            bigger = newImage.isBigger( self.options.width, self.options.height )
            if bigger:
                w, h = newImage.minSize( self.options.size )
                newImage.resize( w, h )
                newImage.cropCenter( self.options.width, self.options.height )
                with open( self.cache, mode='wb' ) as fileout:
                    newImage.saveTo( fileout )

    def checkCacheDir(self):
        if not os.path.exists( self.cache_dir ):
            os.mkdir( self.cache_dir )


class Storage( object ):
    """
    Simple class to list only images on file system and restrict '../' and etc operations
    """
    types = [".jpeg", ".jpg", ]
    path_checkers = ["../", "./", "/.", ]

    def __init__(self, path):
        self.root = settings.VIEWER_STORAGE_PATH
        if self.is_valid_path( path ):
            self.root = os.path.join( self.root, path )
        else:
            raise IOError( "Wrong path'{0}'".format( path ) )


    def list(self, path):
        root = self.join( path )
        if not os.path.exists( root ):
            raise IOError( 'No such directory' )
        objs = os.listdir( root )
        dirs = []
        files = []
        for item in objs:
            if not item.startswith( '.' ):
                file = os.path.join( root, item )
                if os.path.isdir( file ):
                    dirs.append( os.path.join( path, item ) )
                elif self.is_image( item ) and os.path.isfile( file ):
                    files.append( os.path.join( path, item ) )
        return self.build( path, dirs, files )

    def exists(self, path):
        return os.path.exists( self.join( path ) )

    def join(self, path):
        if path != '':
            if not self.is_valid_path( path ):
                raise IOError( 'Bad directory name' )
            return os.path.join( self.root, path )
        return self.root

    def is_image(self, name):
        for item in self.types:
            if name.lower( ).endswith( item ):
                return True
        return False

    def is_valid_path(self, path):
        if path.startswith( '.' ) or path.startswith( '/' ) or path.endswith( '/' ):
            return False
        for item in self.path_checkers:
            if item in path:
                return False
        return True

    @classmethod
    def name(cls, path):
        return os.path.split( path )[1]

    @classmethod
    def build(cls, path, dirs, files):
        back = "/".join( path.split( '/' )[:-1] )
        return {"path": path, "back": back, "dirs": dirs, "files": files}


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
            if time:
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