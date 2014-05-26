# -*- coding: utf-8 -*-
import logging
import re
from django.conf import settings
from django.core.cache import cache
from django.db.models import Q
from django.utils.encoding import smart_text

from bviewer.core.exceptions import FileError
from bviewer.core.files.response import download_response
from bviewer.core.files.storage import ImageStorage
from bviewer.core.images import CacheImage
from bviewer.core.models import Gallery, Video, Image, ProxyUser
from bviewer.core.utils import cache_method, ImageOptions, as_job


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


class BaseController(object):
    def __init__(self, holder, user, uid=None, obj=None):
        """
        :type holder: bviewer.core.models.ProxyUser
        :type user: django.contrib.auth.models.User
        :type uid: str
        """
        self.holder = holder
        self.user = user
        if uid:
            self.uid = uid
        else:
            self.uid = obj.id
        self.obj = obj

    def is_owner(self):
        """
        Return holder == user

        :rtype: bool
        """
        return self.holder == self.user

    def exists(self):
        return bool(self.get_object())

    @staticmethod
    def from_obj(obj):
        raise NotImplementedError()

    def get_object(self):
        raise NotImplementedError()


class GalleryController(BaseController):
    OPEN = Q(visibility=Gallery.VISIBLE) | Q(visibility=Gallery.HIDDEN)

    def _ordering(self, query_set):
        sorting = self.get_object().gallery_sorting
        if sorting == Gallery.ASK:
            return query_set.order_by('time')
        if sorting == Gallery.DESK:
            return query_set.order_by('-time')

    @staticmethod
    def from_obj(obj):
        """
        :type obj: bviewer.core.models.Gallery
        """
        return GalleryController(obj.user, obj.user, obj=obj)

    @cache_method
    def get_object(self):
        """
        Get `pk=uid` with special visibility

        :rtype: bviewer.core.models.Gallery or None
        """
        if self.obj:
            return self.obj
        if self.is_owner():
            return Gallery.objects.safe_get(pk=self.uid, user_id=self.holder.id)
        return Gallery.objects.safe_get(Q(pk=self.uid), Q(user_id=self.holder.id), self.OPEN)

    def _get_galleries(self, parent_id):
        """
        Get galleries where parent `parent_id` with special visibility

        :rtype: django.db.models.query.QuerySet
        """
        if self.is_owner():
            return Gallery.objects.filter(parent_id=parent_id)
        return Gallery.objects.filter(parent_id=parent_id, visibility=Gallery.VISIBLE)

    def get_galleries(self, year=None):
        """
        Get sub galleries `parent=uid` with special visibility and ordering

        :rtype: list of bviewer.core.models.Gallery
        """
        galleries = self._get_galleries(self.uid)
        if year:
            galleries = galleries.filter(time__year=year)
        return list(self._ordering(galleries))

    def get_all_sub_galleries(self, parents=True):
        """
        Get all sub galleries `parent=uid` with special visibility

        :rtype: list of bviewer.core.models.Gallery
        """
        queue = list(self._get_galleries(self.uid))
        result = []
        while queue:
            gallery = queue.pop()
            childes = list(self._get_galleries(gallery.id))
            queue.extend(childes)
            if not (childes and parents is False):
                result.append(gallery)
        return result

    def pre_cache(self):
        ids = [self.get_object().id, ]
        ids.extend(i.id for i in self.get_all_sub_galleries())
        images = Image.objects.filter(gallery__in=ids)
        sizes = [i for i in settings.VIEWER_IMAGE_SIZE.keys() if i != 'full']
        for size in sizes:
            for image in images:
                storage = ImageStorage(self.holder)
                self._pre_cache_image(storage, image, size)

    def _pre_cache_image(self, storage, image, size):
        options = ImageOptions.from_settings(size)
        image_path = storage.get_path(image.path, options)
        if image_path.exists and not image_path.cache_exists:
            image_async = CacheImage(image_path)
            as_job(image_async.process, waite=False)

    def is_archiving_allowed(self):
        return self.get_object().allow_archiving

    def set_archiving(self, value):
        self.get_object().allow_archiving = value
        for gallery in self.get_all_sub_galleries():
            gallery.allow_archiving = value
            gallery.save()

    def is_album(self):
        """
        Is no any sub albums
        :rtype: bool
        """
        return not bool(self.get_galleries())

    def get_images(self):
        """
        Filter images by uid, no any visibility check.
        """
        return Image.objects.filter(gallery=self.uid)

    def get_videos(self):
        """
        Filter videos by uid, no any visibility check.
        """
        return Video.objects.filter(gallery=self.uid)

    def get_available_years(self):
        return list(self._get_galleries(self.uid).datetimes('time', 'year', order='DESC'))


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
        storage = ImageStorage(self.holder)
        options = ImageOptions.from_settings(size)
        image_path = storage.get_path(image.path, options)
        if not image_path.exists:
            raise FileError(smart_text('Image {0} not found').format(image.path))

        if not image_path.cache_exists:
            image_async = CacheImage(image_path)
            as_job(image_async.process)

        return download_response(image_path)


class VideoController(MediaController):
    MODEL = Video

    def get_response(self, size):
        #: :type: bviewer.core.models.Video
        video = self.get_object()
        storage = ImageStorage(self.holder)
        options = ImageOptions.from_settings(size, name=str(video.id))
        image_url = storage.get_url(video.thumbnail_url, options)

        image_async = CacheImage(image_url)
        if not image_url.cache_exists:
            as_job(image_async.download)

        return download_response(image_url)