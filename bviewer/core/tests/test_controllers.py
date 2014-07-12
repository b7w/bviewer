# -*- coding: utf-8 -*-
from django.test import TestCase

from bviewer.core.controllers import AlbumController
from bviewer.core.models import Album, Access
from bviewer.core.tests.data import TestData


class ClearControllersTestCase(TestCase):
    def test_album_controller_params(self):
        data = TestData().load_users().load_galleries()
        gallery = data.gallery_b7w
        top_album = gallery.top_album

        controller = AlbumController(gallery, gallery.user, uid=top_album.id)
        self.assertTrue(controller.is_owner())
        self.assertTrue(controller.user_has_access())

        controller = AlbumController(gallery, None, uid=top_album.id)
        self.assertFalse(controller.is_owner())
        self.assertFalse(controller.user_has_access())


    def test_album_controller_all_sub_albums(self):
        """
        Tests AlbumController.get_all_sub_albums
        """
        data = TestData().load_users().load_galleries()

        gallery = data.gallery_b7w
        top_album = gallery.top_album
        g1 = Album.objects.create(parent=top_album, gallery=gallery, title='1')
        g2 = Album.objects.create(parent=top_album, gallery=gallery, title='2')

        g11 = Album.objects.create(parent=g1, gallery=gallery, title='1.1')
        g12 = Album.objects.create(parent=g1, gallery=gallery, title='1.2')
        g13 = Album.objects.create(parent=g1, gallery=gallery, title='1.3')

        g21 = Album.objects.create(parent=g2, gallery=gallery, title='2.1')
        g22 = Album.objects.create(parent=g2, gallery=gallery, title='2.2')

        g111 = Album.objects.create(parent=g11, gallery=gallery, title='1.1.1')
        g112 = Album.objects.create(parent=g11, gallery=gallery, title='1.1.2')

        g121 = Album.objects.create(parent=g12, gallery=gallery, title='1.2.1')

        controller = AlbumController(gallery, gallery.user, uid=top_album.id)
        albums = controller.get_all_sub_albums()
        self.assertEqual(len(albums), 10)

        controller = AlbumController(gallery, gallery.user, uid=top_album.id)
        albums = controller.get_all_sub_albums(parents=False)
        self.assertEqual(len(albums), 6)


class ControllersTestCase(TestCase):
    def setUp(self):
        super(ControllersTestCase, self).setUp()
        self.data = TestData().load_users().load_galleries().load_albums()

        self.album6 = Album.objects.create(
            parent=self.data.album2, gallery=self.data.gallery_b7w, title='Sub privet'
        )
        self.album7 = Album.objects.create(
            parent=self.data.album_b7w, gallery=self.data.gallery_b7w, title='Hidden',
            visibility=Album.HIDDEN
        )
        self.album8 = Album.objects.create(
            parent=self.album7, gallery=self.data.gallery_b7w, title='Sub hidden'
        )

    def test_album_controller_from_obj(self):
        """
        Tests AlbumController.from_obj
        """
        gallery = self.data.gallery_b7w
        top_album = gallery.top_album

        controller = AlbumController(gallery, gallery.user, uid=top_album.id)
        self.assertEqual(controller.uid, top_album.id)
        self.assertEqual(controller.get_object(), top_album)

        controller = AlbumController.from_obj(top_album)
        self.assertEqual(controller.gallery, gallery)
        self.assertEqual(controller.user, self.data.user_b7w)
        self.assertEqual(controller.uid, top_album.id)
        self.assertEqual(controller.get_object(), top_album)

    def test_album_controller_no_access(self):
        gallery = self.data.gallery_b7w
        album_id = gallery.top_album.id

        cnt = AlbumController(gallery, gallery.user, album_id)
        self.assertEqual(4, len(cnt.get_albums()))
        self.assertEqual(7, len(cnt.get_all_sub_albums()))

        cnt = AlbumController(gallery, self.data.user_keks, album_id)
        self.assertEqual(2, len(cnt.get_albums()))
        self.assertEqual(3, len(cnt.get_all_sub_albums()))

        # test hidden
        cnt = AlbumController(gallery, self.data.user_keks, self.album7.id)
        self.assertTrue(cnt.exists())

        # test privet
        cnt = AlbumController(gallery, self.data.user_keks, self.data.album2.id)
        self.assertFalse(cnt.exists())

    def test_album_controller_has_access(self):
        gallery = self.data.gallery_b7w
        album_id = gallery.top_album.id

        Access.objects.create(user=self.data.user_keks, gallery=gallery)
        cnt = AlbumController(gallery, gallery.user, album_id)
        self.assertEqual(4, len(cnt.get_albums()))
        self.assertEqual(7, len(cnt.get_all_sub_albums()))

        cnt = AlbumController(gallery, self.data.user_keks, album_id)
        self.assertEqual(4, len(cnt.get_albums()))
        self.assertEqual(7, len(cnt.get_all_sub_albums()))

        # test hidden
        cnt = AlbumController(gallery, self.data.user_keks, self.album7.id)
        self.assertTrue(cnt.exists())

        # test privet
        cnt = AlbumController(gallery, self.data.user_keks, self.data.album2.id)
        self.assertTrue(cnt.exists())