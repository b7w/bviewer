# -*- coding: utf-8 -*-
from importlib import import_module

from django.conf import settings
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse, StreamingHttpResponse
from django.utils.encoding import smart_text, smart_bytes


class DjangoDownloadHttpResponse(StreamingHttpResponse):
    def __init__(self, path, name=None):
        """
        :type path: bviewer.core.files.path.ImagePath
        """
        wrapper = FileWrapper(path.cache_open(mode='rb', temp=False))
        super(DjangoDownloadHttpResponse, self).__init__(wrapper)
        name = name or path.name
        self['Content-Type'] = path.content_type
        self['Content-Disposition'] = smart_bytes(smart_text('attachment; filename="{0}"').format(name))
        self['Content-Length'] = path.cache_size


class NginxDownloadHttpResponse(HttpResponse):
    def __init__(self, path, name=None):
        """
        :type path:  bviewer.core.files.path.ImagePath
        """
        super(NginxDownloadHttpResponse, self).__init__()
        name = name or path.name
        url = settings.VIEWER_DOWNLOAD_RESPONSE['INTERNAL_URL'] + '/' + smart_text(path.url)
        self['X-Accel-Charset'] = 'utf-8'
        self['X-Accel-Redirect'] = smart_bytes(url)
        self['Content-Type'] = path.content_type
        self['Content-Disposition'] = smart_bytes(smart_text('attachment; filename="{0}"').format(name))


django = DjangoDownloadHttpResponse
nginx = NginxDownloadHttpResponse


def download_response(path, name=None):
    """
    :type path:  bviewer.core.files.path.ImagePath
    """
    import_path = settings.VIEWER_DOWNLOAD_RESPONSE['BACKEND']
    module_path, class_name = import_path.rsplit('.', 1)
    module = import_module(module_path)
    clazz = getattr(module, class_name)
    return clazz(path, name=name)