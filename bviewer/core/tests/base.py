# -*- coding: utf-8 -*-
from django.core import urlresolvers
from django.test import TestCase

from bviewer.core import settings
from bviewer.core.tests import TestData


class BaseViewTest(TestCase):
    """
    Set up TestData, b7w user as holder.
    """

    def setUp(self):
        self.data = TestData()
        self.data.load_all()
        settings.VIEWER_USER_ID = self.data.user_b7w.id

    def reverse(self, name, *args):
        """
        django.core.urlresolvers.reverse but with *args
        """
        return urlresolvers.reverse(name, args=args)

    def login(self, username=None):
        """
        Login b7w or other `username`
        """
        name = username or self.data.user_b7w.username
        self.assertTrue(self.client.login(username=name, password=self.data.PASSWORD))

    def assertContent(self, url, content):
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(content, resp.content)