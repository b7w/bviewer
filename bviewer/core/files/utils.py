# -*- coding: utf-8 -*-
import logging
import os

logger = logging.getLogger(__name__)


class ImageFolder(object):
    """
    Simple help class to use in views.
    Store `path`, `back` path, sorted `dirs` and `files`
    """

    def __init__(self, path, image_paths):
        """
        :type path: str
        :type image_paths: list of bviewer.core.files.path.ImagePath
        """
        self.path = path
        self.back = os.path.dirname(path)
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


class GalleryConfig(object):
    def __init__(self, gallery, mount):
        self.gallery = gallery
        self.home = mount
        self.url = gallery.url
        self.cache_size = gallery.cache_size
        self.cache_archive_size = gallery.cache_archive_size

    def __str__(self):
        return 'GalleryConfig({0}, {1})'.format(self.gallery, self.home)