# -*- coding: utf-8 -*-
from datetime import datetime
from fractions import Fraction
import os
import random
import logging

from django.conf import settings

from PIL import Image, ImageDraw, ImageFont
from PIL.ExifTags import TAGS


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

    def __init__(self, image):
        """
        :type image: bviewer.core.files.storage.ImagePath
        """
        self.image = image
        self.options = image.options

    def process(self):
        """
        Get image from storage and save it to cache. If image is to big, resize. If to small, link.
        If cache already exists, do nothing
        """
        if not self.image.cache_exists:
            with self.image.open() as fin:
                resize_image = ResizeImage(fin)
                bigger = resize_image.is_bigger(self.options.width, self.options.height)
                if bigger:
                    if self.options.crop:
                        w, h = resize_image.min_size(self.options.size)
                        resize_image.resize(w, h)
                        resize_image.crop_center(self.options.width, self.options.height)
                    else:
                        w, h = resize_image.max_size(self.options.size)
                        resize_image.resize(w, h)
                    with self.image.cache_open() as fout:
                        resize_image.save_to(fout, self.options.quality)

                    # make file creation atomic
                    self.image.rename_temp_cache()
                    logger.info('resize \'%s\' with %s', self.image.path, self.options)
                else:
                    logger.info('link \'%s\' with %s', self.image.path, self.options)
                    self.image.link_to_cache()

    def download(self):
        """
        Download image and put to cache.
        If cache exists, do nothing
        """
        if not self.image.cache_exists:
            with self.image.open() as fin:
                resize_image = ResizeImage(fin)
                bigger = resize_image.is_bigger(self.options.width, self.options.height)
                if bigger:
                    w, h = resize_image.min_size(self.options.size)
                    resize_image.resize(w, h)
                    resize_image.crop_center(self.options.width, self.options.height)
                    with self.image.cache_open() as fout:
                        resize_image.save_to(fout, self.options.quality)

                    # make file creation atomic
                    self.image.rename_temp_cache()
                logger.info('download image \'%s\' %s', self.image, 'and resize' if bigger else '')


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


class RandomImage:
    """
    Create simple square image with color tile background and text on center
    """
    TEXT_FILL = (0, 0, 0)
    FONT_PART = 1.0 / 8

    def __init__(self, size):
        self.size = size
        self.image = Image.new('RGB', (self.size, self.size))
        self._draw = ImageDraw.Draw(self.image)

    def random_color(self):
        return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

    def draw_background(self, tiles):
        self._draw.rectangle((0, 0, self.size, self.size), fill=self.random_color())
        step = self.size / tiles
        for y in range(0, self.size, step):
            for x in range(0, self.size, step):
                self._draw.rectangle((x, y, x + step, y + step), fill=self.random_color())

    def draw_text(self, text):
        font_path = os.path.join(settings.SOURCE_PATH, 'static', 'Ubuntu-RI.ttf')
        font = ImageFont.truetype(font_path, int(self.size * self.FONT_PART))
        text_w, text_h = font.getsize(text)
        x = self.size / 2 - text_w / 2
        y = self.size / 2 - text_h / 2
        self._draw.text((x, y), text, font=font, fill=self.TEXT_FILL)

    def draw(self, text, tiles=16):
        self.draw_background(tiles)
        self.draw_text(text)

    def save(self, path):
        logger.info('Save random image "%s"', path)
        self.image.save(path, 'JPEG')
