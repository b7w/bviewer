# -*- coding: utf-8 -*-
import json

from django.test.client import Client
from rest_framework import status


class ResourceClient(Client):
    content_type = 'application/json'

    def __init__(self, enforce_csrf_checks=False, **defaults):
        super(ResourceClient, self).__init__(enforce_csrf_checks, **defaults)

    def rest_get(self, path, data=None, **kwargs):
        """
        Deserialize result to `response.objects` if many else `response.object`.
        """
        kwargs['HTTP_ACCEPT'] = self.content_type
        if data is not None:
            kwargs['data'] = data

        response = self.get(path, **kwargs)
        assert response.status_code == status.HTTP_200_OK, 'Client.read response.status_code = {0}'.format(response.status_code)
        result = json.loads(response.content)
        if 'results' in result:
            response.objects = result['results']
        else:
            response.object = result

        return response

    def rest_post(self, path, data=None, **kwargs):
        kwargs['content_type'] = self.content_type
        if data is not None:
            kwargs['data'] = json.dumps(data)
        return self.post(path, **kwargs)

    def rest_delete(self, path, data=None, **kwargs):
        if data is not None:
            kwargs['data'] = data
        return self.delete(path, data=data, content_type=self.content_type, **kwargs)