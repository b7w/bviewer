# -*- coding: utf-8 -*-

from bviewer.api.tests.base import BaseResourceTestCase


class PrivateTestCase(BaseResourceTestCase):
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
        # gallery 1 and 5, other private
        response = self.client.read('/api/v1/image/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.objects), 3)

        # plus 2 private
        self.login_user(self.data.user_b7w)
        response = self.client.read('/api/v1/image/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.objects), 5)

        # gallery 1 and 5, other private
        self.login_user(self.data.user_keks)
        response = self.client.read('/api/v1/image/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.objects), 3)

    def test_videos(self):
        # same as images
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

    def test_image_field_path(self):
        url = '/api/v1/image/{0}/'.format(self.data.image1.id)
        response = self.client.read(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('path', response.object)

        self.login_user(self.data.user_b7w)
        response = self.client.read(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('path', response.object)

        self.login_user(self.data.user_keks)
        response = self.client.read(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('path', response.object)
