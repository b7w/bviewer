# -*- coding: utf-8 -*-
import json

from django.http import HttpResponse

from bviewer.core.files.storage import Folder, File


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Folder):
            value = obj.__dict__
            value['split_path'] = [dict(name=k, path=v) for k, v in obj.split_path()]
            return obj.__dict__
        elif isinstance(obj, File):
            return obj.__dict__
        else:
            return json.JSONEncoder.default(self, obj)


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
        return json.dumps(content, cls=JSONEncoder, indent=2)