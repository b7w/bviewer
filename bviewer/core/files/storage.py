# -*- coding: utf-8 -*-
import logging
import os

from bviewer.core import settings
from bviewer.core.exceptions import FileError

logger = logging.getLogger(__name__)


class File(object):
    """
    Store full `path`, `name` and `checked` flag.
    """

    def __init__(self, root, name, saved=False):
        """
        Get folder path and file name.

        :type root: str
        :type name: str
        """
        self.path = os.path.join(root, name)
        self.name = name
        self.saved = saved

    def __lt__(self, other):
        return self.name < other.name


class Folder(object):
    """
    Store `path`, `back` path, sorted `dirs` and `files`
    """

    def __init__(self, path, dirs, files):
        """
        :type path: str
        :type dirs: list of File
        :type files: list of File
        """
        self.path = path
        self.back = "/".join(path.split('/')[:-1])
        self.dirs = sorted(dirs)
        self.files = sorted(files)

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


class Storage(object):
    """
    Simple class to list only images on file system and restrict '../' and etc operations
    """
    types = ['.jpeg', '.jpg', ]
    path_checkers = ['../', './', '/.', ]

    def __init__(self, path, images=None):
        self.root = settings.VIEWER_STORAGE_PATH
        self.images = set(i.path for i in images) if images else None
        if self.is_valid_path(path):
            self.root = os.path.join(self.root, path)
        else:
            logger.warning('Wrong path "%s"', path)
            raise FileError('Wrong path "{0}"'.format(path))

    def list(self, path):
        """
        :type path: str
        :rtype: Folder
        """
        root = self.join(path)
        if not os.path.exists(root):
            logger.warning('No such directory "%s"', root)
            raise FileError('No such directory')
        items = os.listdir(root)
        dirs = []
        files = []
        for item in items:
            if not item.startswith('.'):
                fname = os.path.join(root, item)
                if os.path.isdir(fname):
                    dirs.append(File(path, item))
                elif self.is_image(item) and os.path.isfile(fname):
                    item = File(path, item)
                    if self.images and item.path in self.images:
                        item.saved = True
                    files.append(item)
        return Folder(path, dirs, files)

    def exists(self, path):
        return os.path.exists(self.join(path))

    def join(self, path):
        if path != '':
            if not self.is_valid_path(path):
                logger.warning('Bad directory name "%s"', path)
                raise FileError('Bad directory name')
            return os.path.join(self.root, path)
        return self.root

    def is_image(self, name):
        for item in self.types:
            if name.lower().endswith(item):
                return True
        return False

    def is_valid_path(self, path):
        if path.startswith('.') or path.startswith('/') or path.endswith('/'):
            return False
        for item in self.path_checkers:
            if item in path:
                return False
        return True

    @classmethod
    def name(cls, path):
        return os.path.split(path)[1]
