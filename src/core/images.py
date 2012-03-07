# -*- coding: utf-8 -*-
import os
import urllib2
import cStringIO
from PIL import Image

from core import settings
from core.utils import FileUniqueName

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