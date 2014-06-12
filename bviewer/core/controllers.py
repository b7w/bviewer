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
from bviewer.core.models import Album, Video, Image, ProxyUser
from bviewer.core.utils import cache_method, ImageOptions, as_job


logger = logging.getLogger(__name__)

domain_match = re.compile(r'([w]{3})?\.?(?P<domain>[\w\.]+):?(\d{0,4})')


def get_album_user(request):
    """
    Get domain from request and try to find user with user.url == domain.
    If not try return authenticated user, else user from settings.VIEWER_USER_ID.

    :type request: django.http.HttpRequest
    :rtype: bviewer.core.models.ProxyUser
    """
    key = 'core.utils.get_album_user({0})'.format(request.get_host())
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


class AlbumController(BaseController):
    OPEN = Q(visibility=Album.VISIBLE) | Q(visibility=Album.HIDDEN)

    def _ordering(self, query_set):
        sorting = self.get_object().album_sorting
        if sorting == Album.ASK:
            return query_set.order_by('time')
        if sorting == Album.DESK:
            return query_set.order_by('-time')

    @staticmethod
    def from_obj(obj):
        """
        :type obj: bviewer.core.models.Album
        """
        return AlbumController(obj.user, obj.user, obj=obj)

    @cache_method
    def get_object(self):
        """
        Get `pk=uid` with special visibility

        :rtype: bviewer.core.models.Album or None
        """
        if self.obj:
            return self.obj
        if self.is_owner():
            return Album.objects.safe_get(pk=self.uid, user_id=self.holder.id)
        return Album.objects.safe_get(Q(pk=self.uid), Q(user_id=self.holder.id), self.OPEN)

    def _get_albums(self, parent_id):
        """
        Get albums where parent `parent_id` with special visibility

        :rtype: django.db.models.query.QuerySet
        """
        if self.is_owner():
            return Album.objects.filter(parent_id=parent_id)
        return Album.objects.filter(parent_id=parent_id, visibility=Album.VISIBLE)

    def get_albums(self, year=None):
        """
        Get sub albums `parent=uid` with special visibility and ordering

        :rtype: list of bviewer.core.models.Album
        """
        albums = self._get_albums(self.uid)
        if year:
            albums = albums.filter(time__year=year)
        return list(self._ordering(albums))

    def get_all_sub_albums(self, parents=True):
        """
        Get all sub albums `parent=uid` with special visibility

        :rtype: list of bviewer.core.models.Album
        """
        queue = list(self._get_albums(self.uid))
        result = []
        while queue:
            album = queue.pop()
            childes = list(self._get_albums(album.id))
            queue.extend(childes)
            if not (childes and parents is False):
                result.append(album)
        return result

    def pre_cache(self):
        ids = [self.get_object().id, ]
        ids.extend(i.id for i in self.get_all_sub_albums())
        images = Image.objects.filter(album__in=ids)
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
        for album in self.get_all_sub_albums():
            album.allow_archiving = value
            album.save()

    def is_album(self):
        """
        Is no any sub albums
        :rtype: bool
        """
        return not bool(self.get_albums())

    def get_images(self):
        """
        Filter images by uid, no any visibility check.
        """
        return Image.objects.filter(album=self.uid)

    def get_videos(self):
        """
        Filter videos by uid, no any visibility check.
        """
        return Video.objects.filter(album=self.uid)

    def get_available_years(self):
        return list(self._get_albums(self.uid).datetimes('time', 'year', order='DESC'))


class MediaController(BaseController):
    OPEN = Q(album__visibility=Album.VISIBLE) | Q(album__visibility=Album.HIDDEN)
    MODEL = None

    @cache_method
    def get_object(self):
        """
        Get self.MODEL instance or None
        """
        if self.is_owner():
            return self.MODEL.objects.safe_get(pk=self.uid, album__user__id=self.holder.id)
        return self.MODEL.objects.safe_get(Q(pk=self.uid), Q(album__user__id=self.holder.id), self.OPEN)

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