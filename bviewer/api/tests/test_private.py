# -*- coding: utf-8 -*-
from django.utils.encoding import smart_text
from rest_framework import status

from bviewer.api.tests.base import BaseResourceTestCase


class PrivateTestCase(BaseResourceTestCase):
    def test_albums(self):
        # 2 users home + 4 + 1 b7w private
        response = self.client.rest_get('/api/v1/album/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.objects), 6)

        # check detail private album Unauthorized
        response = self.client.get('/api/v1/album/{0}/'.format(self.data.album2.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.login_user(self.data.user_b7w)
        response = self.client.rest_get('/api/v1/album/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.objects), 7)

        self.login_user(self.data.user_keks)
        response = self.client.rest_get('/api/v1/album/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.objects), 6)

    def test_images(self):
        # album 1 and 5, other private
        response = self.client.rest_get('/api/v1/image/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.objects), 3)

        # check detail private album Unauthorized
        response = self.client.get('/api/v1/image/{0}/'.format(self.data.image3.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # plus 2 private
        self.login_user(self.data.user_b7w)
        response = self.client.rest_get('/api/v1/image/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.objects), 5)

        # album 1 and 5, other private
        self.login_user(self.data.user_keks)
        response = self.client.rest_get('/api/v1/image/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.objects), 3)

    def test_videos(self):
        # same as images
        response = self.client.rest_get('/api/v1/video/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.objects), 3)

        # check detail private album Unauthorized
        response = self.client.get('/api/v1/video/{0}/'.format(self.data.video3.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.login_user(self.data.user_b7w)
        response = self.client.rest_get('/api/v1/video/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.objects), 5)

        self.login_user(self.data.user_keks)
        response = self.client.rest_get('/api/v1/video/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.objects), 3)

    def test_image_field_path(self):
        url = '/api/v1/image/{0}/'.format(self.data.image1.id)
        key = smart_text('path')
        response = self.client.rest_get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(key, response.object)

        self.login_user(self.data.user_b7w)
        response = self.client.rest_get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(key, response.object)

        self.login_user(self.data.user_keks)
        response = self.client.rest_get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(key, response.object)
