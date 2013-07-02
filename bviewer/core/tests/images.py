# -*- coding: utf-8 -*-
from django.test import TestCase
from mock import Mock

from bviewer.core.tests.data import TestData


class CacheImageTest(TestCase):
    def setUp(self):
        self.data = TestData()
        self.path = 'image1.jpg'
        self.user = Mock(url='b7w.dev.loc', home='')
        self.data.generate_image(self.user.home, self.path)