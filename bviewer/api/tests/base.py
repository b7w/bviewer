# -*- coding: utf-8 -*-
from django.conf import settings
from django.test import TestCase

from bviewer.api.tests.client import ResourceClient
from bviewer.core.tests import TestData


class BaseResourceTestCase(TestCase):
    def setUp(self):
        settings.TEST = True

        self.client = ResourceClient()
        self.data = TestData()
        self.data.load_all()

    def login_user(self, user):
        self.assertTrue(self.client.login(username=user.username, password=TestData.PASSWORD))