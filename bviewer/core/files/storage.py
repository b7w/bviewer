# -*- coding: utf-8 -*-
from contextlib import contextmanager
import hashlib
import logging
import os
import uuid
import zipfile

try:
    from urllib2 import urlopen
except ImportError:
    from urllib.request import urlopen

from django.utils.encoding import smart_bytes
from six import BytesIO

from bviewer.core import settings
from bviewer.core.utils import cache_method

logger = logging.getLogger(__name__)


class ImageFolder(object):
    """
    Simple help class to use in views.
    Store `path`, `back` path, sorted `dirs` and `files`
    """

    def __init__(self, path, image_paths):
        """
        :type path: str
        :type image_paths: list of ImagePath
        """
        self.path = path
        self.back = '/'.join(path.split('/')[:-1])
        self.dirs = sorted(i for i in image_paths if i.is_dir)
        self.files = sorted(i for i in image_paths if i.is_image)

    @property
    def split_path(self):
        """
        Split path for folders name with path fot this name.

        Example::

            /r/p1/p2 -> r:/r, p1:/r/p2, p2:/r/p1/p2

        :rtype: list of (str,str)
        """

        def _split(path, data):
            name = os.path.basename(path)
            if name:
                second = os.path.dirname(path)
                data = _split(second, data)
                data.append((name, path))
                return data
            return data

        return _split(self.path, [])


class ImagePathCacheMixin(object):
    """
    Provide operation on cache files. Unique name, tnp name, move, link, exists
    """

    storage = NotImplemented
    path = NotImplemented
    options = None

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
    def cache_exists(self):
        return self.storage.exists(self.cache_name, for_cache=True)

    @property
    @cache_method
    def cache_name_temp(self):
        return self.storage.gen_temp_name() + self.CACHE_FILE_TYPE + '.tmp'

    @property
    def cache_ctime(self):
        return self.storage.ctime(self.cache_name_temp, for_cache=True)

    def cache_open(self, mode='wb'):
        return self.storage.open(self.cache_name_temp, mode=mode, for_cache=True)

    def rename_temp_cache(self):
        self.storage.rename_cache(self.cache_name_temp, self.cache_name)

    def link_to_cache(self):
        self.storage.link_to_cache(self.path, self.cache_name)


class ImagePath(ImagePathCacheMixin):
    """
    Provide basic operation on files, and cache.
    """

    CACHE_FILE_TYPE = '.jpg'

    def __init__(self, storage, path, options=None):
        """
        Get storage and related file path.
        Options is used to get unique file names.

        :type storage: ImageStorage
        :type options: bviewer.core.utils.ResizeOptions
        """
        self.storage = storage
        self.path = path
        self.options = options
        self.name = os.path.basename(path)
        self.parent = os.path.dirname(path)
        self.saved = False

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
    def url(self):
        return os.path.join(self.storage.holder.url, self.cache_name)

    @property
    def ctime(self):
        return self.storage.ctime(self.name)

    def open(self, mode='r'):
        return self.storage.open(self.path, mode=mode)

    def __lt__(self, other):
        return self.name < other.name


class ImageUrl(ImagePathCacheMixin):
    """
    Provide an opportunity to get image from URL, and cache.
    """

    CACHE_FILE_TYPE = '.jpg'

    def __init__(self, storage, thumbnail_url, options=None):
        """
        Get storage and thumbnail url.
        Options is used to get unique file names.

        :type storage: ImageStorage
        :type options: bviewer.core.utils.ResizeOptions
        """
        self.storage = storage
        self.thumbnail_url = thumbnail_url
        self.options = options
        self.name = os.path.basename(thumbnail_url)

    @property
    def url(self):
        return os.path.join(self.storage.holder.url, self.cache_name)

    @contextmanager
    def open(self, mode=None):
        image = BytesIO()
        image.write(urlopen(self.thumbnail_url).read())
        image.seek(0)
        yield image


class ImageArchivePath(ImagePathCacheMixin):
    CACHE_FILE_TYPE = '.zip'

    def __init__(self, storage, options=None):
        """
        Get storage. Options is used to get unique file names.

        :type storage: ImageStorage
        :type options: bviewer.core.utils.ResizeOptions
        """
        self.storage = storage
        self.options = options

    @property
    def url(self):
        return os.path.join(self.storage.holder.url, self.cache_name)

    @contextmanager
    def cache_open(self, mode='wb'):
        """
        Return new zip file

        :rtype: zipfile.ZipFile
        """
        #TODO: look behavior
        with self.storage.open(self.cache_name_temp, mode=mode, for_cache=True) as f:
            with zipfile.ZipFile(f, 'w', zipfile.ZIP_DEFLATED) as z:
                yield z


class ImageStorage(object):
    """
    Wrapper on file system.
    Provide methods to get pre config ImagePath, ImageUrl, ImageArchivePath.
    Allow list directory.
    """

    TYPES_ALLOWED = ('.jpeg', '.jpg', )

    def __init__(self, holder, root_path=None, cache_path=None):
        """
        :param root_path: place where image files stored, default settings.VIEWER_STORAGE_PATH
        :param cache_path: place where cache stored, default settings.VIEWER_CACHE_PATH
        :type holder: bviewer.core.models.ProxyUser
        """
        self.holder = holder
        self.root = root_path or settings.VIEWER_STORAGE_PATH
        self.cache_path = cache_path or settings.VIEWER_CACHE_PATH

        self._root_path = os.path.join(self.root, holder.home)
        self._cache_path = os.path.join(self.cache_path, holder.url)
        self.create_cache()

    def list(self, path=None, saved_images=None):
        out = []
        abs_path = os.path.join(self._root_path, path) if path else self._root_path
        for file_name in os.listdir(abs_path):
            relative_path = os.path.join(path, file_name)
            image_path = ImagePath(self, relative_path)
            if image_path.is_image or image_path.is_dir:
                if saved_images and image_path.path in saved_images:
                    image_path.saved = True
                out.append(image_path)

        return out

    def get_path(self, path, options=None):
        return ImagePath(self, path, options)

    def get_url(self, url, options=None):
        return ImageUrl(self, url, options)

    def get_archive(self, options=None):
        return ImageArchivePath(self, options)

    def is_file(self, path):
        return os.path.isfile(os.path.join(self._root_path, path))

    def is_dir(self, path):
        return os.path.isdir(os.path.join(self._root_path, path))

    def ctime(self, path, for_cache=False):
        root = self._cache_path if for_cache else self._root_path
        return os.path.getctime(os.path.join(root, path))

    def exists(self, path, for_cache=False):
        root = self._cache_path if for_cache else self._root_path
        return os.path.exists(os.path.join(root, path))

    def open(self, path, mode='r', for_cache=False):
        root = self._cache_path if for_cache else self._root_path
        return open(os.path.join(root, path), mode=mode)

    def create_cache(self):
        if not os.path.exists(self._cache_path):
            os.makedirs(self._cache_path)

    def rename_cache(self, path_from, path_to):
        root = self._cache_path
        abs_to = os.path.join(root, path_to)
        if not os.path.lexists(abs_to):
            os.rename(os.path.join(root, path_from), abs_to)

    def link_to_cache(self, path_from, path_to):
        abs_from = os.path.join(self._root_path, path_from)
        abs_to = os.path.join(self._cache_path, path_to)
        os.symlink(abs_from, abs_to)

    def hash_for(self, content):
        return hashlib.sha1(smart_bytes(content)).hexdigest()

    def gen_temp_name(self):
        return uuid.uuid1().hex