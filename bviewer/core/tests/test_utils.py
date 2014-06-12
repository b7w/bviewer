# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from mock import Mock

from django.conf import settings
from django.test import TestCase

from bviewer.core.controllers import domain_match, get_gallery
from bviewer.core.models import Gallery


def request_mock(host, user=None):
    mock = Mock()
    mock.get_host = lambda: host
    mock.user = user if user else Mock(is_authenticated=lambda: False)
    return mock


class UtilsTestCase(TestCase):
    def test_re_domain(self):
        """
        Tests domain match
        """
        match = domain_match.match('demo.test.local')
        self.assertTrue(match)
        self.assertEqual(match.groups(), (None, 'demo.test.local', ''))

        match = domain_match.match('www.demo.test.local')
        self.assertTrue(match)
        self.assertEqual(match.groups(), ('www', 'demo.test.local', ''))

        match = domain_match.match('demo.test.local:8000')
        self.assertTrue(match)
        self.assertEqual(match.groups(), (None, 'demo.test.local', '8000'))

        match = domain_match.match('172.17.1.10:80')
        self.assertTrue(match)
        self.assertEqual(match.groups(), (None, '172.17.1.10', '80'))

    def test_album_user(self):
        """
        Tests get_album_user
        """
        settings.VIEWER_GALLERY_ID = None
        user = User.objects.create_user('User', 'user@user.com', 'test')
        gallery = Gallery.objects.create(user=user)

        request = request_mock('user.example.com')
        obj = get_gallery(request)
        self.assertEqual(obj, gallery)

        request = request_mock('www.user.example.com:8000')
        obj = get_gallery(request)
        self.assertEqual(obj, gallery)

        request = request_mock('user.example.com')
        obj = get_gallery(request)
        self.assertEqual(obj, gallery)

        request = request_mock('example.com')
        obj = get_gallery(request)
        self.assertIsNone(obj)

        settings.VIEWER_GALLERY_ID = gallery.id
        request = request_mock('example.com')
        obj = get_gallery(request)
        self.assertEqual(obj, gallery)