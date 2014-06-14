# -*- coding: utf-8 -*-
from bviewer.core.exceptions import FileError
from bviewer.core.files.base import BaseImageStorage
from bviewer.core.files.path import MountPath
from bviewer.core.files.storage import ImageStorage
from bviewer.core.files.utils import GalleryConfig


class ProxyImageStorage(BaseImageStorage):
    def __init__(self, gallery, root_path=None, cache_path=None, archive_cache=False):
        """
        :param root_path: place where image files stored, default settings.VIEWER_STORAGE_PATH
        :param cache_path: place where cache stored, default settings.VIEWER_CACHE_PATH
        :param archive_cache: set 'archives' sub cache folder instead of 'images'
        :type gallery: bviewer.core.models.Gallery
        """
        self.gallery = gallery
        self.mounts = gallery.home.split(';')
        self.configs = [GalleryConfig(gallery, i) for i in self.mounts]
        self.storages = {}
        for conf in self.configs:
            storage = ImageStorage(conf, root_path=root_path, cache_path=cache_path, archive_cache=archive_cache)
            self.storages[conf.home] = storage

    def _get_storage(self, path):
        for mount in self.mounts:
            if path.startswith(mount):
                if path == mount:
                    return self.storages[mount], ''
                return self.storages[mount], path.replace(mount + '/', '')
        raise FileError('No storage mount found')

    def list(self, path=None, saved_images=None):
        if not path:
            return sorted(MountPath(i) for i in self.mounts)
        storage, path = self._get_storage(path)
        return storage.list(path=path, saved_images=saved_images)

    def get_path(self, path, options=None):
        storage, path = self._get_storage(path)
        return storage.get_path(path, options=options)

    def get_url(self, url, options=None):
        storage = list(self.storages.values())[0]
        return storage.get_path(url, options=options)

    def get_archive(self, options=None):
        storage = list(self.storages.values())[0]
        return storage.get_archive(options=options)

    def clear_cache(self, full=False):
        for storage in self.storages:
            storage.clear_cache(full=full)

    def cache_size(self):
        return sum(i.cache_size() for i in self.storages.values())

    def __repr__(self):
        return 'ProxyImageStorage({0})'.format(self.gallery)