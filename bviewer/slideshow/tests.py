# -*- coding: utf-8 -*-
from django.conf import settings
from rest_framework import status

from bviewer.api.tests.base import BaseResourceTestCase
from bviewer.slideshow.models import SlideShow


class SlideShowTestCase(BaseResourceTestCase):
    def test_get_or_create_checks(self):
        response = self.client.rest_get('/api/v1/actions/slideshow/get_or_create/', check_status=False)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.error, 'No "album" parameter')

        response = self.client.get('/api/v1/actions/slideshow/get_or_create/?album=None')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_or_create(self):
        # Force create session
        self.client.cookies[settings.SESSION_COOKIE_NAME] = 'session_test'

        album_id = self.data.user_b7w.top_album.id
        response = self.client.rest_get('/api/v1/actions/slideshow/get_or_create/?album={0}'.format(album_id))
        obj1 = SlideShow.objects.safe_get(id=response.object['id'])
        self.assertIsNotNone(obj1)
        self.assertEqual(obj1.album_id, album_id)
        self.assertEqual(obj1.status, SlideShow.BUILD)
        self.assertEqual(obj1.image_count, 1)

        response = self.client.rest_get('/api/v1/actions/slideshow/get_or_create/?album={0}'.format(album_id))
        obj2 = SlideShow.objects.safe_get(id=response.object['id'])
        self.assertIsNotNone(obj2)
        self.assertEqual(obj2.status, SlideShow.BUILD)

        self.assertEqual(SlideShow.objects.all().count(), 1)
        obj2.status = SlideShow.FINISHED
        obj2.save()

        response = self.client.rest_get('/api/v1/actions/slideshow/get_or_create/?album={0}'.format(album_id))
        obj3 = SlideShow.objects.safe_get(id=response.object['id'])
        self.assertIsNotNone(obj3)
        self.assertEqual(SlideShow.objects.all().count(), 2)
        self.assertNotEqual(obj3, obj2)

        response = self.client.rest_get('/api/v1/actions/slideshow/get_or_create/?album={0}'.format(self.data.album1.id))
        obj4 = SlideShow.objects.safe_get(id=response.object['id'])
        self.assertIsNotNone(obj4)
        self.assertEqual(obj4.album, self.data.album1)
        self.assertEqual(SlideShow.objects.all().count(), 3)

    def test_get_or_create_login(self):
        self.login_user(self.data.user_b7w)
        self.test_get_or_create()

    def test_next(self):
        response = self.client.rest_get('/api/v1/slideshow/None/next/', check_status=False)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.error, 'No slideshow with id "None"')

        obj = SlideShow.objects.create(
            album=self.data.user_b7w.top_album,
            user=self.data.user_b7w,
            session_key=self.client.session.session_key,
        )

        url = '/api/v1/slideshow/{0}/next/'.format(obj.id)
        response = self.client.rest_get(url)
        self.assertIsNotNone(response.object['title'])
        self.assertIsNotNone(response.object['image_id'])
        self.assertIsNotNone(response.object['link'])

        response = self.client.rest_get(url)
        self.assertIsNotNone(response.object['title'])

        response = self.client.rest_get(url, check_status=False)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        obj = SlideShow.objects.get(id=obj.id)
        self.assertEqual(obj.status, SlideShow.FINISHED)
