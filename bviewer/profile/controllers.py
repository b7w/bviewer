# -*- coding: utf-8 -*-

from bviewer.core.files import Storage
from bviewer.core.models import Image


class ImageController(object):
    """
    List storage and update checked=True images that store in DB.
    Add/Remove images from DB if call `setChecked` method.
    """

    def __init__(self, gallery, user):
        """
        Get Gallery id and ProxyUser
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
        """
        self.folder = self.storage.list(path)

    def setChecked(self, checked):
        """
        Get list of checked image paths in path/
        Add or remove DB and checked difference from DB.
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
        Return Folder
        """
        checked = self.checked if self.checked else self.images_path
        for file in self.folder.files:
            if file.path in checked:
                file.checked = True
        return self.folder