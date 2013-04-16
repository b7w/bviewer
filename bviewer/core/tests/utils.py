# -*- coding: utf-8 -*-
from mock import Mock

from django.test import TestCase

from bviewer.core import settings
from bviewer.core.controllers import get_gallery_user
from bviewer.core.models import ProxyUser
from bviewer.core.utils import domain_match


def request_mock(host, user=None):
    mock = Mock()
    mock.get_host = lambda: host
    mock.user = user if user else Mock(is_authenticated=lambda: False)
    return mock


class UtilsTest(TestCase):
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

    def test_gallery_user(self):
        """
        Tests get_gallery_user
        """
        settings.VIEWER_USER_ID = None
        user = ProxyUser.objects.create(username='User')

        request = request_mock('user.example.com')
        holder = get_gallery_user(request)
        self.assertEqual(holder, user)

        request = request_mock('www.user.example.com:8000')
        holder = get_gallery_user(request)
        self.assertEqual(holder, user)

        request = request_mock('user.example.com')
        holder = get_gallery_user(request)
        self.assertEqual(holder, user)

        request = request_mock('example.com')
        holder = get_gallery_user(request)
        self.assertIsNone(holder)

        settings.VIEWER_USER_ID = user.id
        request = request_mock('example.com')
        holder = get_gallery_user(request)
        self.assertEqual(holder, user)