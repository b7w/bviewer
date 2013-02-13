# -*- coding: utf-8 -*-

from django.test import TestCase

from bviewer.api.tests.client import ResourceClient
from bviewer.core import settings
from bviewer.core.tests.data import TestData


class PrivateTestCase(TestCase):
    def setUp(self):
        settings.TESTS = True
        self.client = ResourceClient()
        self.data = TestData()
        self.data.load_all()

    def login_user(self, user):
        self.assertTrue(self.client.login(username=user.username, password=TestData.PASSWORD))

    def test_galleries(self):
        # 2 users home + 4 + 1 b7w private
        response = self.client.read('/api/v1/gallery/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.objects), 6)

        self.login_user(self.data.user_b7w)
        response = self.client.read('/api/v1/gallery/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.objects), 7)

        self.login_user(self.data.user_keks)
        response = self.client.read('/api/v1/gallery/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.objects), 6)

    def test_images(self):
        response = self.client.read('/api/v1/image/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.objects), 3)

        self.login_user(self.data.user_b7w)
        response = self.client.read('/api/v1/image/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.objects), 5)

        self.login_user(self.data.user_keks)
        response = self.client.read('/api/v1/image/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.objects), 3)

    def test_videos(self):
        response = self.client.read('/api/v1/video/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.objects), 3)

        self.login_user(self.data.user_b7w)
        response = self.client.read('/api/v1/video/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.objects), 5)

        self.login_user(self.data.user_keks)
        response = self.client.read('/api/v1/video/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.objects), 3)
