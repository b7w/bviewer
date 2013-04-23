# -*- coding: utf-8 -*-
import os

from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse
from django.utils.importlib import import_module

from bviewer.core import settings


class DjangoDownloadHttpResponse(HttpResponse):
    def __init__(self, path, name):
        path = os.path.join(settings.VIEWER_CACHE_PATH, path)
        wrapper = FileWrapper(open(path))
        super(DjangoDownloadHttpResponse, self).__init__(wrapper)
        self['Content-Type'] = settings.VIEWER_DOWNLOAD_RESPONSE.get('Content-Type', 'image/jpeg')
        self['Content-Disposition'] = 'attachment; filename="%s"' % name.encode('utf-8')
        self['Content-Length'] = os.path.getsize(path)


class NginxDownloadHttpResponse(HttpResponse):
    def __init__(self, path, name):
        super(NginxDownloadHttpResponse, self).__init__()
        url = settings.VIEWER_DOWNLOAD_RESPONSE['INTERNAL_URL'] + '/' + path.encode('utf-8')
        self['X-Accel-Charset'] = 'utf-8'
        self['X-Accel-Redirect'] = url
        self['Content-Type'] = settings.VIEWER_DOWNLOAD_RESPONSE.get('Content-Type', 'image/jpeg')
        self['Content-Disposition'] = 'attachment; filename="%s"' % name.encode('utf-8')


django = DjangoDownloadHttpResponse
nginx = NginxDownloadHttpResponse


def download_response(path, name):
    import_path = settings.VIEWER_DOWNLOAD_RESPONSE['BACKEND']
    module_path, class_name = import_path.rsplit('.', 1)
    module = import_module(module_path)
    clazz = getattr(module, class_name)
    return clazz(path, name)