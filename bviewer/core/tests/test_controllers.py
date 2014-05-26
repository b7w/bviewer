# -*- coding: utf-8 -*-
from django.test import TestCase

from bviewer.core.controllers import GalleryController
from bviewer.core.models import Gallery
from bviewer.core.tests.data import TestData


class ControllersTestCase(TestCase):
    def test_gallery_controller_all_sub_galleries(self):
        """
        Tests GalleryController.get_all_sub_galleries
        """
        data = TestData()
        data.load_users()

        user = data.user_b7w
        top_gallery = user.top_gallery
        g1 = Gallery.objects.create(parent=top_gallery, user=user, title='1')
        g2 = Gallery.objects.create(parent=top_gallery, user=user, title='2')

        g11 = Gallery.objects.create(parent=g1, user=user, title='1.1')
        g12 = Gallery.objects.create(parent=g1, user=user, title='1.2')
        g13 = Gallery.objects.create(parent=g1, user=user, title='1.3')

        g21 = Gallery.objects.create(parent=g2, user=user, title='2.1')
        g22 = Gallery.objects.create(parent=g2, user=user, title='2.2')

        g111 = Gallery.objects.create(parent=g11, user=user, title='1.1.1')
        g112 = Gallery.objects.create(parent=g11, user=user, title='1.1.2')

        g121 = Gallery.objects.create(parent=g12, user=user, title='1.2.1')

        controller = GalleryController(user, user, top_gallery.id)
        galleries = controller.get_all_sub_galleries()
        self.assertEqual(len(galleries), 10)

        controller = GalleryController(user, user, top_gallery.id)
        galleries = controller.get_all_sub_galleries(parents=False)
        self.assertEqual(len(galleries), 6)

    def test_gallery_controller_from_obj(self):
        """
        Tests GalleryController.from_obj
        """
        data = TestData()
        data.load_users()

        user = data.user_b7w
        top_gallery = user.top_gallery

        controller = GalleryController(user, user, uid=top_gallery.id)
        self.assertEqual(controller.uid, top_gallery.id)
        self.assertIsNone(controller.obj)
        self.assertEqual(controller.get_object(), top_gallery)

        controller = GalleryController(user, user, obj=top_gallery)
        self.assertEqual(controller.uid, top_gallery.id)
        self.assertEqual(controller.obj, top_gallery)
        self.assertEqual(controller.get_object(), top_gallery)


