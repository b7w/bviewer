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

    def test_galleries(self):
        response = self.client.read('/api/v1/gallery/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(5, len(response.objects))

        self.client.login(username='B7W', password='pass')
        response = self.client.read('/api/v1/gallery/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(6, len(response.objects))

    def test_images(self):
        response = self.client.read('/api/v1/image/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(2, len(response.objects))

        self.client.login(username='B7W', password='pass')
        response = self.client.read('/api/v1/image/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(4, len(response.objects))

    def test_images(self):
        response = self.client.read('/api/v1/video/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(2, len(response.objects))

        self.client.login(username='B7W', password='pass')
        response = self.client.read('/api/v1/video/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(4, len(response.objects))
