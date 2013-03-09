# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.utils import simplejson

from bviewer.core.files.storage import Folder, File


def redirect(url_name, *args, **kwargs):
    url = reverse(url_name, args=args)
    params = '&'.join('{0}={1}'.format(k, v) for k, v in kwargs.items() if v is not None)
    return HttpResponseRedirect(url + '?' + params)


class JSONEncoder(simplejson.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Folder):
            value = obj.__dict__
            value['split_path'] = [dict(name=k, path=v) for k, v in obj.split_path()]
            return obj.__dict__
        elif isinstance(obj, File):
            return obj.__dict__
        else:
            return simplejson.JSONEncoder.default(self, obj)


class JSONResponse(HttpResponse):
    """
    Facade for HttpResponse that provide simple encode to json
    and some shortcuts for error and success message
    """

    def __init__(self, content, status=None, content_type=None):
        super(JSONResponse, self).__init__(self.dumps(content), "application/json", status, content_type)

    def dumps(self, content):
        """
        Dumps to json with cls=JSONEncoder and indent=2
        """
        return simplejson.dumps(content, cls=JSONEncoder, indent=2)