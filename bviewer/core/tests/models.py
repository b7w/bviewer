# -*- coding: utf-8 -*-

from httplib import HTTPConnection
from urlparse import urlsplit

from django.contrib.auth.models import User
from django.test import TestCase

from bviewer.core.models import ProxyUser, Gallery, Video
from bviewer.core.tests.data import TestData


class ModelTest(TestCase):
    def test_new_gallery_user(self):
        """
        Tests domain match
        """
        ProxyUser.objects.create(username='Test', password='secret')
        self.assertTrue(User.objects.filter(username='Test').exists())
        self.assertTrue(ProxyUser.objects.filter(username='Test').exists())
        self.assertIsNotNone(ProxyUser.objects.get(username='Test').top_gallery)
        self.assertTrue(Gallery.objects.filter(user__username='Test').exists())

        user = ProxyUser.objects.get(username='Test')
        need = [
            'core.change_proxyuser',
            'core.user_holder',
            'core.add_gallery',
            'core.change_gallery',
            'core.delete_gallery',
            'core.add_image',
            'core.change_image',
            'core.delete_image',
            'core.add_video',
            'core.change_video',
            'core.delete_video',
        ]
        self.assertEqual(set(need), user.get_all_permissions())

    def assertHttpOk(self, url):
        """
        Open http connection, send HEAD and assert 200 status
        """
        host = urlsplit(url)
        conn = HTTPConnection(host.netloc, timeout=4)
        conn.request('HEAD', host.path)
        res = conn.getresponse()
        self.assertEqual(res.status, 200)

    def test_video_thumbnail(self):
        """
        Test Vimio 56433514 video and YouTube 7dGGPlZlPQw thumbnails http status.
        Videos can be deleted! Check it first. Anyway it is important test.
        """
        data = TestData().load_users()
        gallery = data.user_b7w.top_gallery

        video1 = Video.objects.create(gallery=gallery, uid='56433514', type=Video.VIMIO)
        self.assertHttpOk(video1.thumbnail_url)

        video2 = Video.objects.create(gallery=gallery, uid='7dGGPlZlPQw', type=Video.YOUTUBE)
        self.assertHttpOk(video2.thumbnail_url)
