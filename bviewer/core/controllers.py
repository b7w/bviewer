# -*- coding: utf-8 -*-
import logging
import re

from django.core.cache import cache
from django.db.models import Q

from bviewer.core import settings
from bviewer.core.files import Storage
from bviewer.core.files.response import download_response
from bviewer.core.images import CacheImage
from bviewer.core.models import Gallery, Video, Image, ProxyUser
from bviewer.core.utils import cache_method, ResizeOptions, as_job


logger = logging.getLogger(__name__)

domain_match = re.compile(r'([w]{3})?\.?(?P<domain>[\w\.]+):?(\d{0,4})')


def get_gallery_user(request):
    """
    Get domain from request and try to find user with user.url == domain.
    If not try return authenticated user, else user from settings.VIEWER_USER_ID.

    :type request: django.http.HttpRequest
    :rtype: bviewer.core.models.ProxyUser
    """
    key = 'core.utils.get_gallery_user({0})'.format(request.get_host())
    data = cache.get(key)
    if data:
        return data
    if settings.VIEWER_USER_ID:
        user = ProxyUser.objects.get(id=settings.VIEWER_USER_ID)
        cache.set(key, user)
        return user

    match = domain_match.match(request.get_host())
    if match:
        url = match.group('domain')
        user = ProxyUser.objects.safe_get(url=url)
        if user:
            cache.set(key, user)
            return user

    if request.user.is_authenticated():
        return ProxyUser.objects.get(id=request.user.id)

    return None


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
        Get self.MODEL instance or None
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
        #: :type: bviewer.core.models.Image
        image = self.get_object()
        name = Storage.name(image.path)

        options = ResizeOptions.from_settings(self.holder, size)
        image_async = CacheImage(image.path, options)
        if not image_async.is_exists():
            as_job(image_async.process)

        return download_response(image_async.url, name)


class VideoController(MediaController):
    MODEL = Video

    def get_response(self, size):
        #: :type: bviewer.core.models.Video
        video = self.get_object()
        name = video.uid + '.jpg'

        options = ResizeOptions.from_settings(self.holder, size, name=str(video.id))
        image_async = CacheImage(video.thumbnail_url, options)
        if not image_async.is_exists():
            as_job(image_async.download)

        return download_response(image_async.url, name)