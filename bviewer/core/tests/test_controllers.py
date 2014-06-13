# -*- coding: utf-8 -*-
from django.test import TestCase

from bviewer.core.controllers import AlbumController
from bviewer.core.models import Album
from bviewer.core.tests.data import TestData


class ControllersTestCase(TestCase):
    def test_album_controller_all_sub_albums(self):
        """
        Tests AlbumController.get_all_sub_albums
        """
        data = TestData()
        data.load_users()
        data.load_galleries()

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

        controller = AlbumController(gallery, gallery, uid=top_album.id)
        albums = controller.get_all_sub_albums()
        self.assertEqual(len(albums), 10)

        controller = AlbumController(gallery, gallery, uid=top_album.id)
        albums = controller.get_all_sub_albums(parents=False)
        self.assertEqual(len(albums), 6)

    def test_album_controller_from_obj(self):
        """
        Tests AlbumController.from_obj
        """
        data = TestData()
        data.load_users()
        data.load_galleries()

        gallery = data.gallery_b7w
        top_album = gallery.top_album

        controller = AlbumController(gallery, gallery, uid=top_album.id)
        self.assertEqual(controller.uid, top_album.id)
        self.assertIsNone(controller.obj)
        self.assertEqual(controller.get_object(), top_album)

        controller = AlbumController(gallery, gallery, obj=top_album)
        self.assertEqual(controller.uid, top_album.id)
        self.assertEqual(controller.obj, top_album)
        self.assertEqual(controller.get_object(), top_album)

        controller = AlbumController.from_obj(gallery)
        self.assertEqual(controller.uid, top_album.id)
        self.assertEqual(controller.obj, top_album)
        self.assertEqual(controller.get_object(), top_album)