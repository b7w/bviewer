# -*- coding: utf-8 -*-
from django.core import urlresolvers
from django.test import TestCase

from bviewer.core import settings
from bviewer.core.tests import TestData


def reverse(name, *args):
    """
    django.core.urlresolvers.reverse but with \*args
    """
    return urlresolvers.reverse(name, args=args)


class PrivateGalleriesTest(TestCase):
    """
    Create private gallery and not.
    Test that only owner have access to private.
    """

    def setUp(self):
        self.data = TestData()
        self.data.load_all()
        settings.VIEWER_USER_ID = self.data.user_b7w.id

    def login(self):
        name = self.data.user_b7w.username
        assert self.client.login(username=name, password=self.data.PASSWORD)

    def assertContent(self, url, content):
        resp = self.client.get(url)
        assert resp.status_code == 200
        assert content in resp.content

    def test_home(self):
        url = reverse('core.home')
        resp = self.client.get(url)
        assert resp.status_code == 200
        assert 'First' in resp.content
        assert 'Second' not in resp.content
        assert 'Third' in resp.content

        self.login()
        self.assertContent(url, 'First')
        self.assertContent(url, 'Second')
        self.assertContent(url, 'Third')

    def test_gallery(self):
        url_first = reverse('core.gallery', self.data.gallery1.id)
        # resp = self.client.get(url_first)
        # print(resp.content)
        self.assertContent(url_first, 'First')
        url_second = reverse('core.gallery', self.data.gallery2.id)
        self.assertContent(url_second, 'Error')

        self.login()
        self.assertContent(url_first, 'First')
        self.assertContent(url_second, 'Second')

    def test_images(self):
        url_first = reverse('core.image', self.data.image1.id)
        self.assertContent(url_first, 'First')
        url_second = reverse('core.image', self.data.image3.id)
        self.assertContent(url_second, 'Error')

        self.login()
        self.assertContent(url_first, 'First')
        self.assertContent(url_second, 'Second')

    def test_download(self):
        # there is no real images - it will redirect to static one
        url_first = reverse('core.download', 'full', self.data.image1.id)
        resp = self.client.get(url_first)
        self.assertEqual(resp.status_code, 302)
        url_second = reverse('core.download', 'full', self.data.image3.id)
        resp = self.client.get(url_second)
        self.assertEqual(resp.status_code, 404)

        self.login()
        url_first = reverse('core.download', 'full', self.data.image1.id)
        resp = self.client.get(url_first)
        self.assertEqual(resp.status_code, 302)
        url_second = reverse('core.download', 'full', self.data.image3.id)
        resp = self.client.get(url_second)
        self.assertEqual(resp.status_code, 302)

    def test_videos(self):
        url_first = reverse('core.video', self.data.video1.id)
        self.assertContent(url_first, 'First')
        url_second = reverse('core.video', self.data.video3.id)
        self.assertContent(url_second, 'Error')

        self.login()
        self.assertContent(url_first, 'First')
        self.assertContent(url_second, 'Second')
