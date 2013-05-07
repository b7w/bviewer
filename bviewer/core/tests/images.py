# -*- coding: utf-8 -*-
from django.test import TestCase
from mock import Mock

from bviewer.core.images import CacheImage, FileImageReader
from bviewer.core.utils import ResizeOptions
from bviewer.core.tests.data import TestData


class CacheImageTest(TestCase):
    def setUp(self):
        self.data = TestData()
        self.path = 'image1.jpg'
        self.user = Mock(url='b7w.dev.loc', home='')
        self.data.generate_image(self.user.home, self.path)

    def test_hash(self):
        options = [
            ResizeOptions(self.user, 32, 32, crop=False, quality=95),
            ResizeOptions(self.user, 64, 32, crop=False, quality=95),
            ResizeOptions(self.user, 32, 64, crop=False, quality=95),
            ResizeOptions(self.user, 32, 32, crop=True, quality=95),
            ResizeOptions(self.user, 32, 32, crop=False, quality=100),
        ]

        hashes = set(CacheImage(self.path, i).hash for i in options)
        self.assertEqual(len(options), len(hashes),
            msg='Check unique hashes for different options')

        option = ResizeOptions(self.user, 128, 128, crop=False, quality=95)
        hash1 = CacheImage(self.path, option).hash
        self.data.generate_image(self.user.home, self.path, force=True)
        hash2 = CacheImage(self.path, option).hash
        self.assertNotEqual(hash1, hash2, msg='Check hash eq after new image creation')

    def process_image(self, test_func=None):
        options_list = [
            ResizeOptions(self.user, 512, 512, crop=False, quality=95),
            ResizeOptions(self.user, 512, 2048, crop=True, quality=95),
            ResizeOptions(self.user, 1024, 2048, crop=False, quality=95),
            ResizeOptions(self.user, 4096, 4096, crop=False, quality=95),
        ]

        for options in options_list:
            test_func(self.path, options)

    def test_process(self):
        def local(path, options):
            cache_image = CacheImage(path, options)
            cache_image.clear_cache()
            self.assertFalse(cache_image.is_exists())

            cache_image.process()
            self.assertTrue(cache_image.is_exists())

            cache_image.clear_cache()
            self.assertFalse(cache_image.is_exists())

        self.process_image(local)

    def test_process(self):
        def local(path, options):
            cache_image = CacheImage(path, options)
            #hack to use FileImageReader
            cache_image.path = cache_image.abs_path
            cache_image.clear_cache()
            self.assertFalse(cache_image.is_exists())

            cache_image.process(reader=FileImageReader)
            self.assertTrue(cache_image.is_exists())

            cache_image.clear_cache()
            self.assertFalse(cache_image.is_exists())

        self.process_image(local)