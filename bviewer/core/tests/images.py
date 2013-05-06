# -*- coding: utf-8 -*-
from django.test import TestCase

from bviewer.core import settings
from bviewer.core.images import CacheImage
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
