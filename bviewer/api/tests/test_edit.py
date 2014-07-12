# -*- coding: utf-8 -*-
from rest_framework import status

from bviewer.api.tests.base import BaseResourceTestCase


class EditTestCase(BaseResourceTestCase):
    def setUp(self):
        super(EditTestCase, self).setUp()
        user_id = self.data.user_b7w.id
        gallery_id = self.data.gallery_b7w.id
        album_id = self.data.album_b7w.id

        self.new_gallery = dict(user=user_id, url='test', description='New gallery', )
        self.new_album = dict(title='New album', gallery=gallery_id)
        self.new_image = dict(path='image1.jpg', album=album_id)
        self.data.generate_image(self.data.gallery_b7w.home, 'image1.jpg')
        self.new_video = dict(uid='123456', title='New', album=album_id)

    def test_public_post(self):
        response = self.client.rest_post('/api/v1/gallery/', data=self.new_gallery)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.rest_post('/api/v1/album/', data=self.new_album)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.rest_post('/api/v1/image/', data=self.new_image)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.rest_post('/api/v1/video/', data=self.new_video)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_login_post(self):
        self.login_user(self.data.user_b7w)
        response = self.client.rest_post('/api/v1/gallery/', data=self.new_gallery)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.rest_post('/api/v1/album/', data=self.new_album)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.rest_post('/api/v1/image/', data=self.new_image)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.rest_post('/api/v1/video/', data=self.new_video)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_public_delete(self):
        response = self.client.rest_delete('/api/v1/gallery/{0}/'.format(self.data.gallery_b7w.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.rest_delete('/api/v1/album/{0}/'.format(self.data.album1.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.rest_delete('/api/v1/image/{0}/'.format(self.data.image1.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.rest_delete('/api/v1/video/{0}/'.format(self.data.video1.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_login_delete(self):
        self.login_user(self.data.user_b7w)
        response = self.client.rest_delete('/api/v1/image/{0}/'.format(self.data.image1.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.rest_delete('/api/v1/video/{0}/'.format(self.data.video1.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.rest_delete('/api/v1/album/{0}/'.format(self.data.album1.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.rest_delete('/api/v1/gallery/{0}/'.format(self.data.gallery_b7w.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)