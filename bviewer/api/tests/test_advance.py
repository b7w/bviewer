# -*- coding: utf-8 -*-
from rest_framework import status

from bviewer.api.tests.base import BaseResourceTestCase


class AdvanceTestCase(BaseResourceTestCase):
    def test_filter_self(self):
        self.login_user(self.data.user_b7w)
        response = self.client.rest_get('/api/v1/gallery/?user__self')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.objects), 1)

        response = self.client.rest_get('/api/v1/album/?user__self')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.objects), 5)

        response = self.client.rest_get('/api/v1/image/?user__self')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.objects), 4)

        response = self.client.rest_get('/api/v1/video/?user__self')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.objects), 4)
