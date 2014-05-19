# -*- coding: utf-8 -*-
from datetime import datetime
from django.utils.timezone import utc

from bviewer.core.images import CacheImage
from bviewer.core.tests.base import BaseImageStorageTestCase
from bviewer.core.tests.data import TestData
from bviewer.core.utils import ImageOptions


class CacheImageTestCase(BaseImageStorageTestCase):
    def setUp(self):
        super(CacheImageTestCase, self).setUp()
        self.data = TestData()
        self.path = 'image1.jpg'
        self.data.generate_image(self.holder.home, self.path)

    def assertCacheImage(self, options, download=False):
        image_path = self.storage.get_path(self.path, options)
        image = CacheImage(image_path)
        if download:
            image.download()
        else:
            image.process()
        self.assertTrue(image_path.cache_exists)

    def test_image(self):
        """
        Very simple test to detect if `small < real < big` options create cache image file
        """
        small_options = ImageOptions(width=1024, height=1024)
        self.assertCacheImage(small_options)
        self.assertCacheImage(small_options, download=True)

        big_options = ImageOptions(width=1024 ** 2, height=1024 ** 2)
        self.assertCacheImage(big_options)
        self.assertCacheImage(big_options, download=True)


class ExifTest(BaseImageStorageTestCase):
    def setUp(self):
        super(ExifTest, self).setUp()
        self.data = TestData()
        self.path = 'image1.jpg'
        self.data.generate_image(self.holder.home, self.path)

    def test_ctime(self):
        exif = self.storage.exif(self.path)
        self.assertIsNone(exif.ctime)

        exif = self.storage.exif(self.path)
        exif._data = dict(DateTimeOriginal='2013:04:14 12:00:01')
        self.assertEqual(exif.ctime, datetime(2013, 4, 14, 12, 0, 1, tzinfo=utc))