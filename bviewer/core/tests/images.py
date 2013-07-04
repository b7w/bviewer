# -*- coding: utf-8 -*-

from bviewer.core.images import CacheImage
from bviewer.core.tests import ImageStorageTestCase
from bviewer.core.tests.data import TestData
from bviewer.core.utils import ResizeOptions


class CacheImageTest(ImageStorageTestCase):
    def setUp(self):
        super(CacheImageTest, self).setUp()
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
        small_options = ResizeOptions(width=1024, height=1024)
        self.assertCacheImage(small_options)
        self.assertCacheImage(small_options, download=True)

        big_options = ResizeOptions(width=1024 ** 2, height=1024 ** 2)
        self.assertCacheImage(big_options)
        self.assertCacheImage(big_options, download=True)