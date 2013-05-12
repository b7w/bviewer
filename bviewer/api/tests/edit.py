# -*- coding: utf-8 -*-

from bviewer.api.tests.base import BaseResourceTestCase


class EditTestCase(BaseResourceTestCase):
    def setUp(self):
        super(EditTestCase, self).setUp()
        user_id = self.data.user_b7w.id
        gallery_id = self.data.gallery_b7w.id

        self.new_gallery = dict(title='New', user='/api/v1/user/{0}/'.format(user_id))
        self.new_image = dict(path='path', gallery='/api/v1/gallery/{0}/'.format(gallery_id))
        self.new_video = dict(uid='123456', title='New', gallery='/api/v1/gallery/{0}/'.format(gallery_id))

    def test_public_post(self):
        response = self.client.rest_post('/api/v1/gallery/', data=self.new_gallery)
        self.assertEqual(response.status_code, 401)

        response = self.client.rest_post('/api/v1/image/', data=self.new_image)
        self.assertEqual(response.status_code, 401)

        response = self.client.rest_post('/api/v1/video/', data=self.new_video)
        self.assertEqual(response.status_code, 401)

    def test_login_post(self):
        self.login_user(self.data.user_b7w)
        response = self.client.rest_post('/api/v1/gallery/', data=self.new_gallery)
        self.assertEqual(response.status_code, 201)

        response = self.client.rest_post('/api/v1/image/', data=self.new_image)
        self.assertEqual(response.status_code, 201)

        response = self.client.rest_post('/api/v1/video/', data=self.new_video)
        self.assertEqual(response.status_code, 201)

    def test_public_delete(self):
        response = self.client.rest_delete('/api/v1/gallery/{0}/'.format(self.data.gallery1.id))
        self.assertEqual(response.status_code, 401)

        response = self.client.rest_delete('/api/v1/image/{0}/'.format(self.data.image1.id))
        self.assertEqual(response.status_code, 401)

        response = self.client.rest_delete('/api/v1/video/{0}/'.format(self.data.video1.id))
        self.assertEqual(response.status_code, 401)

    def test_login_delete(self):
        self.login_user(self.data.user_b7w)
        response = self.client.rest_delete('/api/v1/image/{0}/'.format(self.data.image1.id))
        self.assertEqual(response.status_code, 204)

        response = self.client.rest_delete('/api/v1/video/{0}/'.format(self.data.video1.id))
        self.assertEqual(response.status_code, 204)

        response = self.client.rest_delete('/api/v1/gallery/{0}/'.format(self.data.gallery1.id))
        self.assertEqual(response.status_code, 204)