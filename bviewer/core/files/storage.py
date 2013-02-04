# -*- coding: utf-8 -*-

import os

from bviewer.core import settings

class File(object):
    def __init__(self, root, name):
        self.path = os.path.join(root, name)
        self.name = name
        self.checked = False

    def __lt__(self, other):
        return self.name < other.name


class Folder(object):
    def __init__(self, path, dirs, files):
        self.path = path
        self.back = "/".join(path.split('/')[:-1])
        self.dirs = sorted(dirs)
        self.files = sorted(files)

    def split_path(self):
        """
        Split path for folders name with path fot this name.
        Return list of pairs.

        Example::

            /root/path1/path2 ->
            root:/root, path1:/root/path2, path2:/root/path1/path2
        """

        def _split( path, data ):
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
    types = [".jpeg", ".jpg", ]
    path_checkers = ["../", "./", "/.", ]

    def __init__(self, path):
        self.root = settings.VIEWER_STORAGE_PATH
        if self.is_valid_path(path):
            self.root = os.path.join(self.root, path)
        else:
            raise IOError("Wrong path'{0}'".format(path))


    def list(self, path):
        root = self.join(path)
        if not os.path.exists(root):
            raise IOError('No such directory')
        objs = os.listdir(root)
        dirs = []
        files = []
        for item in objs:
            if not item.startswith('.'):
                file = os.path.join(root, item)
                if os.path.isdir(file):
                    dirs.append(File(path, item))
                elif self.is_image(item) and os.path.isfile(file):
                    files.append(File(path, item))
        return Folder(path, dirs, files)

    def exists(self, path):
        return os.path.exists(self.join(path))

    def join(self, path):
        if path != '':
            if not self.is_valid_path(path):
                raise IOError('Bad directory name')
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
