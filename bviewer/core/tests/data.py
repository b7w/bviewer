# -*- coding: utf-8 -*-
import os

from django.conf import settings
from django.contrib.auth.models import User, Permission

from bviewer.core.images import RandomImage
from bviewer.core.models import Gallery, Album, Image, Video


class TestData(object):
    PASSWORD = 'pass'

    def load_all(self):
        self.load_users()
        self.load_galleries()
        self.load_albums()
        self.load_images()
        self.load_videos()
        return self

    def load_users(self):
        self.user_b7w = User(username='B7W')
        self.user_b7w.set_password(self.PASSWORD)
        self.user_b7w.save()
        self.update_to_gallery('B7W')

        self.user_keks = User(username='Keks')
        self.user_keks.set_password(self.PASSWORD)
        self.user_keks.save()
        self.update_to_gallery('Keks')
        return self

    def update_to_gallery(self, name):
        user = User.objects.get(username=name)
        perm = Permission.objects.get(codename='user_gallery')
        user.user_permissions.add(perm)
        user.save()

    def load_galleries(self):
        self.gallery_b7w = Gallery(user=self.user_b7w)
        self.gallery_b7w.save()
        self.gallery_keks = Gallery(user=self.user_keks)
        self.gallery_keks.save()
        return self

    def load_albums(self):
        self.album_b7w = self.gallery_b7w.top_album
        self.album_keks = self.gallery_keks.top_album

        self.album1 = Album(parent=self.album_b7w, gallery=self.gallery_b7w, title='First')
        self.album1.description = 'First description'
        self.album1.save()

        self.album2 = Album(parent=self.album_b7w, gallery=self.gallery_b7w, title='Second')
        self.album2.visibility = Album.PRIVATE
        self.album2.description = 'Second description'
        self.album2.save()

        self.album3 = Album(parent=self.album_b7w, gallery=self.gallery_b7w, title='Third')
        self.album3.description = 'Third description'
        self.album3.save()

        self.album4 = Album(parent=self.album3, gallery=self.gallery_b7w, title='Under third')
        self.album4.description = 'Under description'
        self.album4.save()

        self.album5 = Album(gallery=self.gallery_keks, title='Hidden')
        self.album5.description = 'Hidden description'
        self.album5.save()
        return self

    def generate_image(self, home, name, force=False):
        """
        Create random image in settings.VIEWER_STORAGE_PATH if not exists.
        Or user `force=True` to override.
        """
        path = os.path.join(settings.VIEWER_STORAGE_PATH, home, name)
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        if not os.path.exists(path) or force:
            image = RandomImage(2048)
            image.draw(name)
            image.save(path)

    def load_images(self):
        self.image1 = Image.objects.create(album=self.album1, path='image1.jpg')
        self.image2 = Image.objects.create(album=self.album1, path='image2.jpg')
        self.generate_image(self.album1.gallery.home, self.image1.path)
        self.generate_image(self.album1.gallery.home, self.image2.path)

        self.image3 = Image.objects.create(album=self.album2, path='image3.jpg')
        self.image4 = Image.objects.create(album=self.album2, path='image4.jpg')
        self.generate_image(self.album2.gallery.home, self.image3.path)
        self.generate_image(self.album2.gallery.home, self.image4.path)

        self.image5 = Image.objects.create(album=self.album5, path='image5.jpg')
        self.generate_image(self.album5.gallery.home, self.image5.path)
        return self

    def load_videos(self):
        self.video1 = Video.objects.create(album=self.album1, uid='video1', type=Video.YOUTUBE)
        self.video2 = Video.objects.create(album=self.album1, uid='video2', type=Video.VIMIO)

        self.video3 = Video.objects.create(album=self.album2, uid='video3', type=Video.YOUTUBE)
        self.video4 = Video.objects.create(album=self.album2, uid='video4', type=Video.VIMIO)

        self.video5 = Video.objects.create(album=self.album5, uid='video5', type=Video.VIMIO)
        return self
