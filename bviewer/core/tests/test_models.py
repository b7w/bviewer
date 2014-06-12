# -*- coding: utf-8 -*-
try:
    from httplib import HTTPConnection
    from urlparse import urlsplit
except ImportError:
    from http.client import HTTPConnection
    from urllib.parse import urlsplit

from django.contrib.auth.models import User
from django.test import TestCase

from bviewer.core.models import Gallery, Album, Video
from bviewer.core.tests.data import TestData


class ModelTestCase(TestCase):
    def test_new_album_user(self):
        """
        Tests domain match
        """
        user = User.objects.create_user('Test', 'test@test.com', 'test')

        Gallery.objects.create(user=user)
        self.assertTrue(User.objects.filter(username='Test').exists())
        self.assertTrue(Gallery.objects.filter(user__username='Test').exists())
        self.assertIsNotNone(Gallery.objects.get(user__username='Test').top_album)
        self.assertTrue(Album.objects.filter(gallery__user__username='Test').exists())

        user = User.objects.get(username='Test')
        need = [
            'core.change_gallery',
            'core.user_gallery',
            'core.add_album',
            'core.change_album',
            'core.delete_album',
            'core.add_image',
            'core.change_image',
            'core.delete_image',
            'core.add_video',
            'core.change_video',
            'core.delete_video',
            'slideshow.add_slideshow',
            'slideshow.change_slideshow',
            'slideshow.delete_slideshow',
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
        data = TestData().load_users().load_galleries()
        album = data.gallery_b7w.top_album

        video1 = Video.objects.create(album=album, uid='56433514', type=Video.VIMIO)
        self.assertHttpOk(video1.thumbnail_url)

        video2 = Video.objects.create(album=album, uid='7dGGPlZlPQw', type=Video.YOUTUBE)
        self.assertHttpOk(video2.thumbnail_url)
