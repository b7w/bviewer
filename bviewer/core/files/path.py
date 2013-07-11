# -*- coding: utf-8 -*-
from contextlib import contextmanager
import logging
import os
import zipfile

try:
    from urllib2 import urlopen
except ImportError:
    from urllib.request import urlopen

from django.utils.six import BytesIO

from bviewer.core.utils import cache_method

logger = logging.getLogger(__name__)


class ImagePathCacheMixin(object):
    """
    Provide operation on cache files. Unique name, tnp name, move, link, exists
    """

    storage = NotImplemented
    path = NotImplemented
    options = NotImplemented

    CACHE_FILE_TYPE = NotImplemented

    @property
    @cache_method
    def cache_name(self):
        option_pack = tuple()
        if self.options:
            option_pack += (self.options.height, self.options.width, self.options.quality, self.options.crop)
            if self.options.name:
                option_pack += (self.options.name,)
            else:
                option_pack += (self.path, self.storage.ctime(self.path),)
        else:
            option_pack += (self.path, self.storage.ctime(self.path),)
        return self.storage.hash_for(option_pack) + self.CACHE_FILE_TYPE

    @property
    @cache_method
    def cache_name_temp(self):
        return self.storage.gen_temp_name() + self.CACHE_FILE_TYPE + '.tmp'

    @property
    def cache_exists(self):
        return self.storage.exists(self.cache_name, for_cache=True)

    @property
    def cache_ctime(self):
        return self.storage.ctime(self.cache_name, for_cache=True)

    @property
    def cache_size(self):
        return self.storage.size(self.cache_name, for_cache=True)

    def cache_open(self, mode='wb', temp=True):
        path = self.cache_name_temp if temp else self.cache_name
        return self.storage.open(path, mode=mode, for_cache=True)

    def rename_temp_cache(self):
        self.storage.rename_cache(self.cache_name_temp, self.cache_name)

    def link_to_cache(self):
        self.storage.link_to_cache(self.path, self.cache_name)


class BasePath(object):
    CACHE_FILE_TYPE = '.jpg'

    def __init__(self, storage, path, options=None):
        """
        Get storage and related file path.
        Options is used to get unique file names.

        :type storage: ImageStorage
        :type options: bviewer.core.utils.ImageOptions
        """
        self.storage = storage
        self.path = path
        self.options = options
        self.name = os.path.basename(path)
        self.saved = False
        self.content_type = 'image/jpeg'

    @property
    def url(self):
        return '/'.join([self.storage.holder.url, self.url_name])

    @property
    def url_name(self):
        raise NotImplementedError()

    @property
    def exists(self):
        raise NotImplementedError()

    def open(self, mode='rb'):
        raise NotImplementedError()


class ImagePath(BasePath, ImagePathCacheMixin):
    """
    Provide basic operation on files, and cache.
    """

    def __init__(self, storage, path, options=None):
        """
        Get storage and related file path.
        Options is used to get unique file names.

        :type storage: ImageStorage
        :type options: bviewer.core.utils.ImageOptions
        """
        super(ImagePath, self).__init__(storage, path, options=options)

    @property
    def url_name(self):
        return self.cache_name

    @property
    def is_image(self):
        if self.storage.is_file(self.path):
            for item in self.storage.TYPES_ALLOWED:
                if self.name.lower().endswith(item):
                    return True
        return False

    @property
    def is_dir(self):
        return self.storage.is_dir(self.path)

    @property
    def exists(self):
        return self.storage.exists(self.path)

    @property
    @cache_method
    def exif(self):
        return self.storage.exif(self.path)

    @property
    def url(self):
        return '/'.join([self.storage.holder.url, self.cache_name])

    @property
    def ctime(self):
        return self.storage.ctime(self.name)

    def open(self, mode='rb'):
        return self.storage.open(self.path, mode=mode)

    def __lt__(self, other):
        return self.name < other.name

    def __repr__(self):
        return 'ImagePath({s}, "{p}", options={o})' \
            .format(s=self.storage, p=self.path, o=self.options)


class ImageUrl(BasePath, ImagePathCacheMixin):
    """
    Provide an opportunity to get image from URL, and cache.
    """

    def __init__(self, storage, thumbnail_url, options=None):
        """
        Get storage and thumbnail url.
        Options is used to get unique file names.

        :type storage: ImageStorage
        :type options: bviewer.core.utils.ImageOptions
        """
        super(ImageUrl, self).__init__(storage, thumbnail_url, options=options)

    @property
    def url_name(self):
        return self.cache_name

    @contextmanager
    def open(self, mode=None):
        image = BytesIO()
        image.write(urlopen(self.path).read())
        image.seek(0)
        yield image


class ImageArchivePath(BasePath, ImagePathCacheMixin):
    CACHE_FILE_TYPE = '.zip'

    def __init__(self, storage, options=None):
        """
        Get storage. Options is used to get unique file names.

        :type storage: ImageStorage
        :type options: bviewer.core.utils.ImageOptions
        """
        super(ImageArchivePath, self).__init__(storage, 'None', options=options)
        self.content_type = 'application/zip'

    @property
    def url_name(self):
        return self.cache_name

    @contextmanager
    def open(self, mode='w'):
        """
        Return new zip file

        :rtype: zipfile.ZipFile
        """
        with self.cache_open(mode=mode + 'b') as f:
            with zipfile.ZipFile(f, mode, zipfile.ZIP_DEFLATED) as z:
                yield z

