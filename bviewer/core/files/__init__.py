# -*- coding: utf-8 -*-
import os

from bviewer.core import settings

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
                    dirs.append(os.path.join(path, item))
                elif self.is_image(item) and os.path.isfile(file):
                    files.append(os.path.join(path, item))
        return self.build(path, dirs, files)

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

    @classmethod
    def build(cls, path, dirs, files):
        dirs.sort()
        files.sort()
        back = "/".join(path.split('/')[:-1])
        return {"path": path, "back": back, "dirs": dirs, "files": files}
