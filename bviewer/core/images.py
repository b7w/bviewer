# -*- coding: utf-8 -*-
from datetime import datetime
from fractions import Fraction
import os
import urllib2
import cStringIO
import logging

from PIL import Image
from PIL.ExifTags import TAGS

from bviewer.core import settings
from bviewer.core.utils import FileUniqueName


logger = logging.getLogger(__name__)


class ResizeImage(object):
    """
    Get file with image. Resize, crop it.
    """

    def __init__(self, filein):
        self.file = Image.open(filein)
        if self.file.mode not in ('L', 'RGB'):
            self.file = self.file.convert('RGB')
        self.quality = 95
        self.type = 'JPEG'

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
        self.file = self.file.resize((width, height), Image.ANTIALIAS)

    def crop(self, x_offset, y_offset, width, height):
        """
        Crop image with ``x_offset``, ``y_offset``, ``width``, ``height``
        """
        self.file = self.file.crop((x_offset, y_offset, width, height))

    def cropCenter(self, width, height):
        """
        Cut out an image with ``width`` and ``height`` of the center
        """
        x_offset = (self.width - width) / 2
        y_offset = (self.height - height) / 2
        self.crop(x_offset, y_offset, x_offset + width, y_offset + height)

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
        return self.width > width and self.height > height

    def minSize(self, value):
        """
        Scale images size where the min size len will be ``value``
        """
        if self.isLandscape():
            scale = float(self.height) / value
            width = int(self.width / scale)
            return width, value
        else:
            scale = float(self.width) / value
            height = int(self.height / scale)
            return value, height

    def maxSize(self, value):
        """
        Scale images size where the max size len will be ``value``
        """
        if self.isPortrait():
            scale = float(self.height) / value
            width = int(self.width / scale)
            return width, value
        else:
            scale = float(self.width) / value
            height = int(self.height / scale)
            return value, height

    def saveTo(self, fileio):
        """
        Save to open file ``fileio``. Need to close by yourself.
        """
        self.file.save(fileio, self.type, quality=self.quality)


class CacheImage(object):
    """
    It is a facade for Resize image that resize images and cache it in `settings.VIEWER_CACHE_PATH`
    """

    def __init__(self, path, options):
        """
        path -> path to image,
        options -> ResizeOptions
        """
        self.path = path
        self.abs_path = os.path.join(settings.VIEWER_STORAGE_PATH, options.storage, path)
        self.options = options
        # each user will have his own cache dir
        self.cache_dir = os.path.join(settings.VIEWER_CACHE_PATH, options.user)

        self.hash = self.get_hash_name()
        self.url = os.path.join(options.user, self.hash + '.jpg')
        self.cache = os.path.join(self.cache_dir, self.hash + '.jpg')

    def get_hash_name(self):
        self.hash_builder = FileUniqueName()
        # if it is a video - there is no file path
        if self.options.name:
            return self.hash_builder.build(self.options.name, extra=self.options.size)
        try:
            time = os.path.getmtime(self.abs_path)
        except OSError as e:
            # TODO: fix this terrible code
            raise IOError(e)
        return self.hash_builder.build(self.path, time=time, extra=self.options.size)

    def process(self):
        """
        Get image from storage and save it to cache. If image is to big, resize. If to small, link.
        If cache already exists, do nothing
        """
        self.check_cache_dir()
        if not os.path.lexists(self.cache):
            with open(self.abs_path, mode='rb') as filein:
                new_image = ResizeImage(filein)
                bigger = new_image.isBigger(self.options.width, self.options.height)
                if bigger:
                    if self.options.crop:
                        w, h = new_image.minSize(self.options.size)
                        new_image.resize(w, h)
                        new_image.cropCenter(self.options.width, self.options.height)
                    else:
                        w, h = new_image.maxSize(self.options.size)
                        new_image.resize(w, h)
                    with open(self.cache, mode='wb') as fileout:
                        new_image.saveTo(fileout)
                    logger.info('resize \'%s\' with %s', self.path, self.options)
                else:
                    logger.info('link \'%s\' with %s', self.path, self.options)
                    os.symlink(self.abs_path, self.cache)

    def download(self):
        """
        Download image and put to cache.
        If cache exists, do nothing
        """
        self.check_cache_dir()
        if not os.path.exists(self.cache):
            image = cStringIO.StringIO()
            image.write(urllib2.urlopen(self.path).read())
            image.seek(0)
            newImage = ResizeImage(image)
            bigger = newImage.isBigger(self.options.width, self.options.height)
            if bigger:
                w, h = newImage.minSize(self.options.size)
                newImage.resize(w, h)
                newImage.cropCenter(self.options.width, self.options.height)
                with open(self.cache, mode='wb') as fileout:
                    newImage.saveTo(fileout)
            logger.info('download image \'%s\' %s', self.path, 'and resize' if bigger else '')

    def check_cache_dir(self):
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)


class Exif(object):
    def __init__(self, fname):
        self.fname = fname
        image = Image.open(fname)
        info = image._getexif()
        if info:
            self._data = dict((TAGS.get(tag, tag), value) for tag, value in info.items())
        else:
            self._data = {}

    @property
    def fnumber(self):
        a, b = self._data.get('FNumber', (0, 1))
        return round(float(a) / b, 1)

    @property
    def exposure(self):
        a, b = self._data.get('ExposureTime', (0, 1))
        return Fraction(a, b)

    @property
    def iso(self):
        return self._data.get('ISOSpeedRatings', 0)

    @property
    def flenght(self):
        a, b = self._data.get('FocalLength', (0, 0))
        return a

    @property
    def model(self):
        return self._data.get('Model', '')

    @property
    def time(self):
        time = self._data.get('DateTime')
        if time:
            try:
                return datetime.strptime(time, '%Y:%m:%d %H:%M:%S')
            except ValueError:
                pass

    def items(self):
        return dict(
            fnumber=self.fnumber,
            exposure=self.exposure,
            iso=self.iso,
            flenght=self.flenght,
            model=self.model,
            time=self.time,
        )

    def __repr__(self):
        return '<Exif{0}>'.format(self.items())