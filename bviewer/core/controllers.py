# -*- coding: utf-8 -*-
import logging

from django.db.models import Q
from bviewer.core.files import Storage
from bviewer.core.files.serve import DownloadResponse
from bviewer.core.images import CacheImageAsync

from bviewer.core.models import Gallery, Video, Image
from bviewer.core.utils import cache_method, ResizeOptions

logger = logging.getLogger(__name__)


class BaseController:
    def __init__(self, holder, user, uid):
        """
        :type holder: bviewer.core.models.ProxyUser
        :type user: django.contrib.auth.models.User
        :type uid: str
        """
        self.holder = holder
        self.user = user
        self.uid = uid

    def is_owner(self):
        """
        Return holder == user

        :rtype: bool
        """
        return self.holder == self.user

    def get_object(self):
        raise NotImplementedError()


class GalleryController(BaseController):
    OPEN = Q(visibility=Gallery.VISIBLE) | Q(visibility=Gallery.HIDDEN)

    @cache_method
    def get_object(self):
        """
        Get `pk=uid` with special visibility

        :rtype: bviewer.core.models.Gallery or None
        """
        if self.is_owner():
            return Gallery.objects.safe_get(pk=self.uid, user_id=self.holder.id)
        return Gallery.objects.safe_get(Q(pk=self.uid), Q(user_id=self.holder.id), self.OPEN)

    @cache_method
    def get_galleries(self):
        """
        Get sub galleries `parent=uid` with special visibility

        :rtype: list of bviewer.core.models.Gallery
        """
        if self.is_owner():
            return list(Gallery.objects.filter(parent=self.uid))
        return list(Gallery.objects.filter(parent=self.uid, visibility=Gallery.VISIBLE))

    def is_album(self):
        """
        Is no any sub albums
        :rtype: bool
        """
        return not bool(self.get_galleries())

    def get_images(self):
        """
        Filter images by uid, no any visibility check.
        If `is_album` else return []
        """
        if self.is_album():
            return Image.objects.filter(gallery=self.uid)
        return []

    def get_videos(self):
        """
        Filter videos by uid, no any visibility check.
        If `is_album` else return []
        """
        if self.is_album():
            return Video.objects.filter(gallery=self.uid)
        return []


class MediaController(BaseController):
    OPEN = Q(gallery__visibility=Gallery.VISIBLE) | Q(gallery__visibility=Gallery.HIDDEN)
    MODEL = None

    @cache_method
    def get_object(self):
        """
        :rtype: bviewer.core.models.Image or None
        """
        if self.is_owner():
            return self.MODEL.objects.safe_get(pk=self.uid, gallery__user__id=self.holder.id)
        return self.MODEL.objects.safe_get(Q(pk=self.uid), Q(gallery__user__id=self.holder.id), self.OPEN)

    def get_response(self, size):
        """
        Get thumbnail size and return response object
        """
        raise NotImplementedError()


class ImageController(MediaController):
    MODEL = Image

    def get_response(self, size):
        image = self.get_object()
        name = Storage.name(image.path)

        options = ResizeOptions(size, user=self.holder.url, storage=self.holder.home)
        image_async = CacheImageAsync(image.path, options)
        image_async.process()

        return DownloadResponse.build(image_async.url, name)


class VideoController(MediaController):
    MODEL = Video

    def get_response(self, size):
        video = self.get_object()
        name = video.uid + '.jpg'

        options = ResizeOptions(size, user=self.holder.url, storage=self.holder.home, name=str(video.id))
        image_async = CacheImageAsync(video.thumbnail_url, options)
        image_async.download()

        return DownloadResponse.build(image_async.url, name)