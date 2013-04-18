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
from bviewer.core.utils import FileUniqueName, abs_image_path


logger = logging.getLogger(__name__)


class ResizeImage(object):
    """
    Get file with image. Resize, crop it.
    """

    def __init__(self, filein):
        self.file = Image.open(filein)
        if self.file.mode not in ('L', 'RGB'):
            self.file = self.file.convert('RGB')
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
        Resize image to `width` and `width`
        """
        self.file = self.file.resize((width, height), Image.ANTIALIAS)

    def crop(self, x_offset, y_offset, width, height):
        """
        Crop image with `x_offset`, `y_offset`, `width`, `height`
        """
        self.file = self.file.crop((x_offset, y_offset, width, height))

    def crop_center(self, width, height):
        """
        Cut out an image with `width` and `height` of the center
        """
        x_offset = (self.width - width) / 2
        y_offset = (self.height - height) / 2
        self.crop(x_offset, y_offset, x_offset + width, y_offset + height)

    def is_portrait(self):
        """
        Is width < height
        """
        return self.width < self.height

    def is_landscape(self):
        """
        Is width >= height
        """
        return self.width >= self.height

    def is_bigger(self, width, height):
        """
        Is this image bigger that `width` and `height`
        """
        return self.width > width and self.height > height

    def min_size(self, value):
        """
        Scale images size where the min size len will be `value`
        """
        if self.is_landscape():
            scale = float(self.height) / value
            width = int(self.width / scale)
            return width, value
        else:
            scale = float(self.width) / value
            height = int(self.height / scale)
            return value, height

    def max_size(self, value):
        """
        Scale images size where the max size len will be `value`
        """
        if self.is_portrait():
            scale = float(self.height) / value
            width = int(self.width / scale)
            return width, value
        else:
            scale = float(self.width) / value
            height = int(self.height / scale)
            return value, height

    def save_to(self, fout, quality):
        """
        Save to open file. Need to close by yourself.

        :type fout: file
        :type quality: int
        """
        self.file.save(fout, self.type, quality=quality)


class CacheImage(object):
    """
    It is a facade for Resize image that resize images and cache it in `settings.VIEWER_CACHE_PATH`
    """

    def __init__(self, path, options):
        """
        :type path: str
        :type options: bviewer.core.utils.ResizeOptions
        """
        self.path = path
        self.abs_path = abs_image_path(options.storage, path)
        self.options = options
        # each user will have his own cache dir
        self.cache_dir = os.path.join(settings.VIEWER_CACHE_PATH, options.user)

        self.hash = self.get_hash_name()
        self.url = os.path.join(options.user, self.hash + '.jpg')
        self.cache = os.path.join(self.cache_dir, self.hash + '.jpg')

    def get_hash_name(self):
        self.hash_builder = FileUniqueName()
        options = (self.options.size, self.options.quality)
        # if it is a video - there is no file path
        if self.options.name:
            return self.hash_builder.build(self.options.name, extra=options)
        try:
            time = os.path.getmtime(self.abs_path)
        except OSError as e:
            # TODO: fix this terrible code
            raise IOError(e)
        return self.hash_builder.build(self.path, time=time, extra=options)

    def process(self):
        """
        Get image from storage and save it to cache. If image is to big, resize. If to small, link.
        If cache already exists, do nothing
        """
        self.check_cache_dir()
        if not os.path.lexists(self.cache):
            with open(self.abs_path, mode='rb') as filein:
                new_image = ResizeImage(filein)
                bigger = new_image.is_bigger(self.options.width, self.options.height)
                if bigger:
                    if self.options.crop:
                        w, h = new_image.min_size(self.options.size)
                        new_image.resize(w, h)
                        new_image.crop_center(self.options.width, self.options.height)
                    else:
                        w, h = new_image.max_size(self.options.size)
                        new_image.resize(w, h)
                    with open(self.cache, mode='wb') as fout:
                        new_image.save_to(fout, self.options.quality)
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
            bigger = newImage.is_bigger(self.options.width, self.options.height)
            if bigger:
                w, h = newImage.min_size(self.options.size)
                newImage.resize(w, h)
                newImage.crop_center(self.options.width, self.options.height)
                with open(self.cache, mode='wb') as fileout:
                    newImage.save_to(fileout, self.options.quality)
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