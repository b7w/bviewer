# -*- coding: utf-8 -*-
from django.test import TestCase

from bviewer.core import settings
from bviewer.core.images import CacheImage, FileImageReader
from bviewer.core.utils import ResizeOptions
from bviewer.core.tests.data import TestData


class CacheImageTest(TestCase):
    def setUp(self):
        self.data = TestData()
        self.data.load_all()
        settings.VIEWER_USER_ID = self.data.user_b7w.id

    def test_hash(self):
        image = self.data.image1
        user = image.gallery.user

        options = [
            ResizeOptions(user, 32, 32, crop=False, quality=95),
            ResizeOptions(user, 64, 32, crop=False, quality=95),
            ResizeOptions(user, 32, 64, crop=False, quality=95),
            ResizeOptions(user, 32, 32, crop=True, quality=95),
            ResizeOptions(user, 32, 32, crop=False, quality=100),
        ]

        hashes = set(CacheImage(image.path, i).hash for i in options)
        self.assertEqual(len(options), len(hashes),
            msg='Check unique hashes for different options')

        option = ResizeOptions(user, 128, 128, crop=False, quality=95)
        hash1 = CacheImage(image.path, option).hash
        self.data._generate_image(user.home, image.path, force=True)
        hash2 = CacheImage(image.path, option).hash
        self.assertNotEqual(hash1, hash2, msg='Check hash eq after new image creation')

    def process_image(self, test_func=None):
        image = self.data.image1
        user = image.gallery.user

        options_list = [
            ResizeOptions(user, 512, 512, crop=False, quality=95),
            ResizeOptions(user, 512, 2048, crop=True, quality=95),
            ResizeOptions(user, 1024, 2048, crop=False, quality=95),
            ResizeOptions(user, 4096, 4096, crop=False, quality=95),
        ]

        for options in options_list:
            test_func(image, options)

    def test_process(self):
        def local(image, options):
            cache_image = CacheImage(image.path, options)
            cache_image.clear_cache()
            self.assertFalse(cache_image.is_exists())

            cache_image.process()
            self.assertTrue(cache_image.is_exists())

            cache_image.clear_cache()
            self.assertFalse(cache_image.is_exists())

        self.process_image(local)

    def test_process(self):
        def local(image, options):
            cache_image = CacheImage(image.path, options)
            #hack to use FileImageReader
            cache_image.path = cache_image.abs_path
            cache_image.clear_cache()
            self.assertFalse(cache_image.is_exists())

            cache_image.process(reader=FileImageReader)
            self.assertTrue(cache_image.is_exists())

            cache_image.clear_cache()
            self.assertFalse(cache_image.is_exists())

        self.process_image(local)