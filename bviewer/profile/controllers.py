# -*- coding: utf-8 -*-

from bviewer.core.files import Storage
from bviewer.core.models import Image, Video
from bviewer.profile.forms import VideoForm


class ImageController(object):
    """
    List storage and update checked=True images that store in DB.
    Add/Remove images from DB if call `setChecked` method.
    """

    def __init__(self, gallery, user):
        """
        :type gallery: int
        :type user: bviewer.core.models.ProxyUser
        """
        self.gallery = gallery
        self.user = user
        self.storage = Storage(user.home)
        self.images = Image.objects.filter(gallery_id=gallery, gallery__user=user) if gallery else []
        self.images_path = set(map(lambda x: x.path, self.images))
        self.checked = []

    def setPath(self, path):
        """
        List all images in path

        :type path: str
        """
        self.folder = self.storage.list(path)

    def setChecked(self, checked):
        """
        Get list of checked image paths in path.
        Add or remove DB and checked difference from DB.

        :type checked: list of str
        """
        if checked:
            self.checked = set(checked)
            if not (self.checked <= set(self.folder.files)):
                raise IOError('Some files not found in path')

            diff_add = self.checked - self.images_path
            if diff_add:
                Image.objects.bulk_create(
                    map(lambda x: Image(gallery_id=self.gallery, path=x), diff_add)
                )
            diff_del = self.images_path - self.checked
            if diff_del:
                Image.objects.filter(
                    gallery=self.gallery,
                    gallery__user=self.user,
                    path__in=diff_del)\
                .delete()

    def getFolder(self):
        """
        :rtype : bviewer.core.files.storage.Folder
        """
        checked = self.checked if self.checked else self.images_path
        for file in self.folder.files:
            if file.path in checked:
                file.checked = True
        return self.folder


class VideoController(object):
    def __init__(self, gallery, user, video, new):
        """
        :type gallery: int
        :type user: bviewer.core.models.ProxyUser
        :type video: int
        :type new: str
        """
        self.gallery_id = gallery
        self.user = user
        self.video_id = video
        self.new = new
        self.init()

    def init(self):
        if self.new:
            if not self.gallery_id:
                raise ValueError("Select gallery")
            self.video = Video.objects.create(
                uid=self.new,
                type=Video.VIMIO,
                gallery_id=self.gallery_id,
                title='New video',
            )
            self.video_id = self.video.id
        elif self.video_id:
            self.video = Video.objects.get(id=self.video_id, gallery__user=self.user)

    def perform_post_form(self, data):
        """
        Get POST data.

        :raise: ValueError on no video id
        """
        if self.video_id:
            form = VideoForm(data, instance=self.video)
            if form.is_valid():
                form.save()
            return form
        raise ValueError("On post, some video must be selected")

    def perform_get_form(self):
        if self.video_id:
            return VideoForm(instance=self.video)
        return VideoForm()

    def get_videos(self):
        if self.gallery_id:
            return  Video.objects.filter(gallery_id=self.gallery_id, gallery__user=self.user)
        return []