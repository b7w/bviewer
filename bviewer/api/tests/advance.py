# -*- coding: utf-8 -*-

from bviewer.api.tests.base import BaseResourceTestCase


class AdvanceTestCase(BaseResourceTestCase):
    def test_filter_self(self):
        self.login_user(self.data.user_b7w)
        response = self.client.read('/api/v1/gallery/?user=self')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.objects), 5)

        response = self.client.read('/api/v1/image/?gallery__user=self')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.objects), 4)

        response = self.client.read('/api/v1/image/?gallery__user=self')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.objects), 4)
