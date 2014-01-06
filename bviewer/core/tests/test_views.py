# -*- coding: utf-8 -*-
from django.utils.encoding import smart_text

from bviewer.core.tests.base import BaseViewTestCase


class PrivateGalleriesTestCase(BaseViewTestCase):
    """
    Create private gallery and not.
    Test that only owner have access to private.
    """

    def test_home(self):
        url = self.reverse('core.home')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('First', smart_text(resp.content))
        self.assertNotIn('Second', smart_text(resp.content))
        self.assertIn('Third', smart_text(resp.content))

        self.login()
        self.assertContent(url, 'First')
        self.assertContent(url, 'Second')
        self.assertContent(url, 'Third')

    def test_gallery(self):
        url_first = self.reverse('core.gallery', self.data.gallery1.id)
        self.assertContent(url_first, 'First')
        url_second = self.reverse('core.gallery', self.data.gallery2.id)
        self.assertContent(url_second, 'Error')

        self.login()
        self.assertContent(url_first, 'First')
        self.assertContent(url_second, 'Second')

    def test_images(self):
        url_first = self.reverse('core.image', self.data.image1.id)
        self.assertContent(url_first, 'First')
        url_second = self.reverse('core.image', self.data.image3.id)
        self.assertContent(url_second, 'Error')

        self.login()
        self.assertContent(url_first, 'First')
        self.assertContent(url_second, 'Second')

    def test_download(self):
        url_first = self.reverse('core.download', 'full', self.data.image1.id)
        resp = self.client.get(url_first)
        self.assertEqual(resp.status_code, 200)
        url_second = self.reverse('core.download', 'full', self.data.image3.id)
        resp = self.client.get(url_second)
        self.assertEqual(resp.status_code, 404)

        self.login()
        url_first = self.reverse('core.download', 'full', self.data.image1.id)
        resp = self.client.get(url_first)
        self.assertEqual(resp.status_code, 200)
        url_second = self.reverse('core.download', 'full', self.data.image3.id)
        resp = self.client.get(url_second)
        self.assertEqual(resp.status_code, 200)

    def test_videos(self):
        url_first = self.reverse('core.video', self.data.video1.id)
        self.assertContent(url_first, 'First')
        url_second = self.reverse('core.video', self.data.video3.id)
        self.assertContent(url_second, 'Error')

        self.login()
        self.assertContent(url_first, 'First')
        self.assertContent(url_second, 'Second')
