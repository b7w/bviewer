# -*- coding: utf-8 -*-
import os
import shutil
from mock import Mock

from django.conf import settings
from django.core import urlresolvers
from django.test import TestCase
from django.utils.encoding import smart_text

from bviewer.core.files.storage import ImageStorage
from bviewer.core.tests.data import TestData


class BaseViewTestCase(TestCase):
    """
    Set up TestData, b7w user as holder.
    """

    def setUp(self):
        settings.TEST = True

        if os.path.exists(settings.VIEWER_CACHE_PATH):
            shutil.rmtree(settings.VIEWER_CACHE_PATH)

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
        self.assertIn(content, smart_text(resp.content))


class BaseImageStorageTestCase(TestCase):
    def setUp(self):
        self.holder = Mock(home='holder_home', url='holder_url', cache_size=0)
        self.storage = ImageStorage(self.holder)
        self.remove_storage_folders()
        self.create_storage_folders()

    def create_storage_folders(self):
        if not os.path.exists(self.storage._abs_root_path):
            os.makedirs(self.storage._abs_root_path)
        if not os.path.exists(self.storage._abs_cache_path):
            os.makedirs(self.storage._abs_cache_path)

    def remove_storage_folders(self):
        if os.path.exists(self.storage._abs_root_path):
            shutil.rmtree(self.storage._abs_root_path)
        if os.path.exists(self.storage._abs_cache_path):
            shutil.rmtree(self.storage._abs_cache_path)