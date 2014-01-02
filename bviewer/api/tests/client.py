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
        If check_status=False, no status code check perform and error saved in response.error.
        """
        check_status = kwargs.pop('check_status', True)
        kwargs['HTTP_ACCEPT'] = self.content_type
        if data is not None:
            kwargs['data'] = data

        response = self.get(path, **kwargs)
        if check_status:
            assert_message = 'response.status_code = {0}'.format(response.status_code)
            assert response.status_code == status.HTTP_200_OK, assert_message
        result = json.loads(response.content) if response.content else {}
        if 'results' in result:
            response.objects = result['results']
        elif 'error' in result:
            response.error = result['error']
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