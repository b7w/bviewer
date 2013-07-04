# -*- coding: utf-8 -*-
import os

from django.contrib.auth.models import User, Permission

from bviewer.core import settings
from bviewer.core.images import RandomImage
from bviewer.core.models import ProxyUser, Gallery, Image, Video


class TestData:
    PASSWORD = 'pass'

    def load_all(self):
        self.load_users()
        self.load_galleries()
        self.load_images()
        self.load_videos()

    def load_users(self):
        self.user_b7w = ProxyUser(username='B7W')
        self.user_b7w.set_password(self.PASSWORD)
        self.user_b7w.save()
        self.update_to_holder('B7W')

        self.user_keks = ProxyUser(username='Keks')
        self.user_keks.set_password(self.PASSWORD)
        self.user_keks.save()
        self.update_to_holder('Keks')
        return self

    def update_to_holder(self, name):
        user = User.objects.get(username=name)
        perm = Permission.objects.get(codename='user_holder')
        user.user_permissions.add(perm)
        user.save()

    def load_galleries(self):
        self.gallery_b7w = self.user_b7w.top_gallery
        self.gallery_keks = self.user_keks.top_gallery

        self.gallery1 = Gallery(parent=self.gallery_b7w, user=self.user_b7w, title='First')
        self.gallery1.description = 'First description'
        self.gallery1.save()

        self.gallery2 = Gallery(parent=self.gallery_b7w, user=self.user_b7w, title='Second')
        self.gallery2.visibility = Gallery.PRIVATE
        self.gallery2.description = 'Second description'
        self.gallery2.save()

        self.gallery3 = Gallery(parent=self.gallery_b7w, user=self.user_b7w, title='Third')
        self.gallery3.description = 'Third description'
        self.gallery3.save()

        self.gallery4 = Gallery(parent=self.gallery3, user=self.user_b7w, title='Under third')
        self.gallery4.description = 'Under description'
        self.gallery4.save()

        self.gallery5 = Gallery(user=self.user_keks, title='Hidden')
        self.gallery5.description = 'Hidden description'
        self.gallery5.save()
        return self

    def generate_image(self, home, name, force=False):
        """
        Create random image in settings.VIEWER_STORAGE_PATH if not exists.
        Or user `force=True` to override.
        """
        path = os.path.join(settings.VIEWER_STORAGE_PATH, home, name)
        if not os.path.exists(path) or force:
            image = RandomImage(2048)
            image.draw(name)
            image.save(path)

    def load_images(self):
        self.image1 = Image.objects.create(gallery=self.gallery1, path='image1.jpg')
        self.image2 = Image.objects.create(gallery=self.gallery1, path='image2.jpg')
        self.generate_image(self.gallery1.user.home, self.image1.path)
        self.generate_image(self.gallery1.user.home, self.image2.path)

        self.image3 = Image.objects.create(gallery=self.gallery2, path='image3.jpg')
        self.image4 = Image.objects.create(gallery=self.gallery2, path='image4.jpg')
        self.generate_image(self.gallery2.user.home, self.image3.path)
        self.generate_image(self.gallery2.user.home, self.image4.path)

        self.image5 = Image.objects.create(gallery=self.gallery5, path='image5.jpg')
        self.generate_image(self.gallery5.user.home, self.image5.path)
        return self

    def load_videos(self):
        self.video1 = Video.objects.create(gallery=self.gallery1, uid='video1', type=Video.YOUTUBE)
        self.video2 = Video.objects.create(gallery=self.gallery1, uid='video2', type=Video.VIMIO)

        self.video3 = Video.objects.create(gallery=self.gallery2, uid='video3', type=Video.YOUTUBE)
        self.video4 = Video.objects.create(gallery=self.gallery2, uid='video4', type=Video.VIMIO)

        self.video5 = Video.objects.create(gallery=self.gallery5, uid='video5', type=Video.VIMIO)
        return self
