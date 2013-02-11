# -*- coding: utf-8 -*-

from django.contrib.auth.models import User, Permission

from bviewer.core.models import ProxyUser, Gallery, Image, Video


class TestData:
    def load_all(self):
        self.load_users()
        self.load_galleries()
        self.load_images()
        self.load_videos()

    def load_users(self):
        self.user_b7w = ProxyUser(username='B7W')
        self.user_b7w.set_password('pass')
        self.user_b7w.save()
        self.update_to_holder('B7W')

    def update_to_holder(self, name):
        b7w = User.objects.get(username=name)
        perm = Permission.objects.get(codename='user_holder')
        b7w.user_permissions.add(perm)
        b7w.save()

    def load_galleries(self):
        self.gallery_top = self.user_b7w.top_gallery

        self.gallery1 = Gallery(parent=self.gallery_top, user=self.user_b7w, title='First')
        self.gallery1.description = 'First description'
        self.gallery1.save()

        self.gallery2 = Gallery(parent=self.gallery_top, user=self.user_b7w, title='Second')
        self.gallery2.private = True
        self.gallery2.description = 'Second description'
        self.gallery2.save()

        self.gallery3 = Gallery(parent=self.gallery_top, user=self.user_b7w, title='Third')
        self.gallery3.description = 'Third description'
        self.gallery3.save()

        self.gallery4 = Gallery(parent=self.gallery3, user=self.user_b7w, title='Under third')
        self.gallery4.description = 'Under description'
        self.gallery4.save()

        self.gallery5 = Gallery(user=self.user_b7w, title='Hidden')
        self.gallery5.description = 'Hidden description'
        self.gallery5.save()

    def load_images(self):
        self.image1 = Image.objects.create(gallery=self.gallery1, path='image1.jpg')
        self.image2 = Image.objects.create(gallery=self.gallery1, path='image2.jpg')

        self.image3 = Image.objects.create(gallery=self.gallery2, path='image3.jpg')
        self.image4 = Image.objects.create(gallery=self.gallery2, path='image4.jpg')

    def load_videos(self):
        self.video1 = Video.objects.create(gallery=self.gallery1, uid='video1', type=Video.YOUTUBE)
        self.video2 = Video.objects.create(gallery=self.gallery1, uid='video2', type=Video.VIMIO)

        self.video3 = Video.objects.create(gallery=self.gallery2, uid='video3', type=Video.YOUTUBE)
        self.video4 = Video.objects.create(gallery=self.gallery2, uid='video4', type=Video.VIMIO)