# -*- coding: utf-8 -*-

from django.core import urlresolvers
from django.test import TestCase

from bviewer.core import settings
from bviewer.core.models import ProxyUser, Gallery, Image, Video


def reverse( name, *args):
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
        settings.TESTS = True
        self.user = ProxyUser(username='B7W', email='b7w', is_active=True)
        self.user.set_password('root')
        self.user.save()

        self.gallery_first = Gallery.objects.create(
            title='First',
            user=self.user,
            parent=self.user.top_gallery
        )
        self.image_first = Image.objects.create(gallery=self.gallery_first)
        self.video_first = Video.objects.create(gallery=self.gallery_first)
        self.gallery_second = Gallery.objects.create(
            title='Second',
            user=self.user,
            parent=self.user.top_gallery,
            private=True
        )
        self.image_second = Image.objects.create(gallery=self.gallery_second)
        self.video_second = Video.objects.create(gallery=self.gallery_second)

    def login(self):
        assert self.client.login(username='B7W', password='root')

    def assertContent(self, url, content):
        resp = self.client.get(url)
        assert resp.status_code == 200
        assert content in resp.content

    def test_home(self):
        url = reverse('core.home', 'b7w')
        resp = self.client.get(url)
        assert resp.status_code == 200
        assert 'First' in resp.content
        assert 'Second' not in resp.content

        self.login()
        self.assertContent(url, 'First')
        self.assertContent(url, 'Second')

    def test_gallery(self):
        url_first = reverse('core.gallery', 'b7w', self.gallery_first.id)
        self.assertContent(url_first, 'First')
        url_second = reverse('core.gallery', 'b7w', self.gallery_second.id)
        self.assertContent(url_second, 'Error')

        self.login()
        self.assertContent(url_first, 'First')
        self.assertContent(url_second, 'Second')

    def test_images(self):
        url_first = reverse('core.image', 'b7w', self.image_first.id)
        self.assertContent(url_first, 'First')
        url_second = reverse('core.image', 'b7w', self.image_second.id)
        self.assertContent(url_second, 'Error')

        self.login()
        self.assertContent(url_first, 'First')
        self.assertContent(url_second, 'Second')

    def test_download(self):
        url_first = reverse('core.download', 'b7w', 'full', self.image_first.id)
        resp = self.client.get(url_first)
        resp.status = 200
        url_second = reverse('core.download', 'b7w', 'full', self.image_second.id)
        resp = self.client.get(url_second)
        resp.status = 404

        self.login()
        url_first = reverse('core.download', 'b7w', 'full', self.image_first.id)
        resp = self.client.get(url_first)
        resp.status = 200
        url_second = reverse('core.download', 'b7w', 'full', self.image_second.id)
        resp = self.client.get(url_second)
        resp.status = 200

    def test_videos(self):
        url_first = reverse('core.video', 'b7w', self.video_first.id)
        self.assertContent(url_first, 'First')
        url_second = reverse('core.video', 'b7w', self.video_second.id)
        self.assertContent(url_second, 'Error')

        self.login()
        self.assertContent(url_first, 'First')
        self.assertContent(url_second, 'Second')
