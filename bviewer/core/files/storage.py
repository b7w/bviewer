# -*- coding: utf-8 -*-
import hashlib
import logging
import os
import shutil
import uuid

try:
    from urllib2 import urlopen
except ImportError:
    from urllib.request import urlopen

from django.utils.encoding import smart_bytes

from bviewer.core import settings
from bviewer.core.files.path import ImagePath, ImageUrl, ImageArchivePath
from bviewer.core.exceptions import FileError
from bviewer.core.images import Exif

logger = logging.getLogger(__name__)


class ImageStorage(object):
    """
    Wrapper on file system.
    Provide methods to get pre config ImagePath, ImageUrl, ImageArchivePath.
    Allow list directory.
    """

    TYPES_ALLOWED = ('.jpeg', '.jpg', )
    PATH_CHECKERS = ('../', './', '/.', )

    def __init__(self, holder, root_path=None, cache_path=None, archive_cache=False):
        """
        :param root_path: place where image files stored, default settings.VIEWER_STORAGE_PATH
        :param cache_path: place where cache stored, default settings.VIEWER_CACHE_PATH
        :param archive_cache: set 'archives' sub cache folder instead of 'images'
        :type holder: bviewer.core.models.ProxyUser
        """
        self.holder = holder
        self.root = root_path or settings.VIEWER_STORAGE_PATH
        self.cache_path = cache_path or settings.VIEWER_CACHE_PATH

        self._abs_root_path = os.path.join(self.root, holder.home)
        if archive_cache:
            self._abs_cache_path = os.path.join(self.cache_path, 'archives', holder.url)
            self._max_cache_size = holder.cache_archive_size * 2 ** 20
        else:
            self._abs_cache_path = os.path.join(self.cache_path, 'images', holder.url)
            self._max_cache_size = holder.cache_size * 2 ** 20
        self.create_cache()

    def _is_valid_path(self, path):
        if path.startswith('.') or path.startswith('/') or path.endswith('/'):
            return False
        for item in self.PATH_CHECKERS:
            if item in path:
                return False
        return True

    def list(self, path=None, saved_images=None):
        """
        Return list of sorted ImagePath. If path is not - list `self.root_path`.
        If `saved_images` declared with paths, saved=True will be check on equal paths.

        :type saved_images: set of str
        :rtype: list of ImagePath
        """
        out = []
        path = path or ''
        if not self._is_valid_path(path):
            raise FileError('Invalid "{p}" path'.format(p=path))
        abs_path = os.path.join(self._abs_root_path, path) if path else self._abs_root_path
        if not os.path.exists(abs_path):
            raise FileError('Directory "{p}" not exists'.format(p=path))

        for file_name in os.listdir(abs_path):
            relative_path = os.path.join(path, file_name)
            image_path = ImagePath(self, relative_path)
            if image_path.is_image or image_path.is_dir:
                if saved_images and image_path.path in saved_images:
                    image_path.saved = True
                out.append(image_path)

        return sorted(out)

    def get_path(self, path, options=None):
        return ImagePath(self, path, options)

    def get_url(self, url, options=None):
        return ImageUrl(self, url, options)

    def get_archive(self, options=None):
        return ImageArchivePath(self, options)

    def is_file(self, path):
        return os.path.isfile(os.path.join(self._abs_root_path, path))

    def is_dir(self, path):
        return os.path.isdir(os.path.join(self._abs_root_path, path))

    def ctime(self, path, for_cache=False):
        root = self._abs_cache_path if for_cache else self._abs_root_path
        return os.path.getctime(os.path.join(root, path))

    def size(self, path, for_cache=False):
        root = self._abs_cache_path if for_cache else self._abs_root_path
        return os.path.getsize(os.path.join(root, path))

    def exists(self, path, for_cache=False):
        root = self._abs_cache_path if for_cache else self._abs_root_path
        return os.path.exists(os.path.join(root, path))

    def exif(self, path):
        return Exif(os.path.join(self._abs_root_path, path))

    def open(self, path, mode='r', for_cache=False):
        root = self._abs_cache_path if for_cache else self._abs_root_path
        return open(os.path.join(root, path), mode=mode)

    def create_cache(self):
        if not os.path.exists(self._abs_cache_path):
            os.makedirs(self._abs_cache_path)

    def clear_cache(self, full=False):
        """
        Clear old cache while size of directory bigger than holder.cache_size.
        If `full` is True - delete user cache folder.
        """
        abs_cache = self._abs_cache_path
        if os.path.exists(abs_cache):
            if full:
                shutil.rmtree(abs_cache)
            else:
                cache_paths = [os.path.join(abs_cache, i) for i in os.listdir(abs_cache)]
                cache_paths = [i for i in cache_paths if not os.path.islink(i)]
                cache_paths = sorted(cache_paths, key=os.path.getctime, reverse=True)
                while sum(map(os.path.getsize, cache_paths)) > self._max_cache_size:
                    os.remove(cache_paths.pop())

    def rename_cache(self, path_from, path_to):
        abs_from = os.path.join(self._abs_cache_path, path_from)
        abs_to = os.path.join(self._abs_cache_path, path_to)
        if os.path.exists(abs_from) and not os.path.lexists(abs_to):
            os.rename(abs_from, abs_to)

    def link_to_cache(self, path_from, path_to):
        abs_from = os.path.join(self._abs_root_path, path_from)
        abs_to = os.path.join(self._abs_cache_path, path_to)
        if hasattr(os, 'symlink'):
            os.symlink(abs_from, abs_to)
        else:
            shutil.copyfile(abs_from, abs_to)

    def hash_for(self, content):
        return hashlib.sha1(smart_bytes(content)).hexdigest()

    def gen_temp_name(self):
        return uuid.uuid1().hex

    def __repr__(self):
        return 'ImageStorage({h})'.format(h=self.holder)