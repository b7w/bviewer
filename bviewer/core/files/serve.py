# -*- coding: utf-8 -*-

import os

from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse
from django.utils.importlib import import_module

from bviewer.core import settings


class DownloadResponse:
    """
    Response that make X-Accel-Redirect for supported web server or serve file.
    """

    @classmethod
    def get_backend(cls):
        """
        Return file serving backend
        """
        import_path = settings.VIEWER_SERVE['BACKEND']
        dot = import_path.rindex('.')
        module, class_name = import_path[:dot], import_path[dot + 1:]
        mod = import_module(module)
        return getattr(mod, class_name)

    @classmethod
    def build(cls, path, name):
        """
        Return HttpResponse object with file
        or instruction to http server where file exists.
        """
        Backend = cls.get_backend()
        backend = Backend(settings.VIEWER_SERVE)
        response = backend.generate(path, name)

        return response


class BaseDownloadResponse:
    """
    self.settings - dict settings.LIMITED_SERVE
    plus default values such as content_type
    """

    def __init__(self, settings):
        self.settings = settings
        if 'Content-Type' not in self.settings:
            self.settings['Content-Type'] = 'image/jpeg'

    def generate(self, path, name):
        """
        Return HttpResponse obj.
        path and name better to encode utf-8
        """
        raise NotImplementedError()


class nginx(BaseDownloadResponse):
    """
    Nginx X-Accel-Redirect backend
    """

    def generate(self, path, name):
        response = HttpResponse()
        url = self.settings['INTERNAL_URL'] + '/' + path.encode('utf-8')
        response['X-Accel-Charset'] = 'utf-8'
        response['X-Accel-Redirect'] = url
        response['Content-Type'] = self.settings['Content-Type']
        response['Content-Disposition'] = 'attachment; filename="%s"' % name.encode('utf-8')
        return response


class default(BaseDownloadResponse):
    """
    Django serving backend
    """

    def generate(self, path, name):
        path = os.path.join(settings.VIEWER_CACHE_PATH, path)
        wrapper = FileWrapper(open(path))
        response = HttpResponse(wrapper)
        response['Content-Type'] = self.settings['Content-Type']
        response['Content-Disposition'] = 'attachment; filename="%s"' % name.encode('utf-8')
        response['Content-Length'] = os.path.getsize(path)
        return response