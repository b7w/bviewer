# -*- coding: utf-8 -*-

from django.test.client import Client
from tastypie.serializers import Serializer


class ResourceClient(Client):
    content_type = 'application/json'

    def __init__(self, enforce_csrf_checks=False, **defaults):
        super(ResourceClient, self).__init__(enforce_csrf_checks, **defaults)
        self.serializer = Serializer()

    def rest_get(self, path, data=None, **kwargs):
        """
        Method to interact with tastypie rest api. Send GET, only JSON.
        Deserialize result to `response.meta` and `response.objects` if `'meta' and 'objects' in result`.
        Else `response.object = result`.
        """
        kwargs['HTTP_ACCEPT'] = self.content_type
        if data is not None:
            kwargs['data'] = data

        response = self.get(path, **kwargs)
        assert response.status_code == 200, 'Client.read response.status_code = {0}'.format(response.status_code)
        result = self.serializer.deserialize(response.content, format=self.content_type)
        if 'meta' in result and 'objects' in result:
            response.meta = result['meta']
            response.objects = result['objects']
        else:
            response.object = result

        return response

    def rest_post(self, path, data=None, **kwargs):
        """
        Method to interact with tastypie rest api. Send POST, only JSON.
        """
        kwargs['content_type'] = self.content_type
        if data is not None:
            kwargs['data'] = self.serializer.serialize(data, format=self.content_type)
        return self.post(path, **kwargs)

    def rest_delete(self, path, data=None, **kwargs):
        """
        Method to interact with tastypie rest api. Send DELETE, only JSON.
        """
        if data is not None:
            kwargs['data'] = data
        return self.delete(path, data=data, content_type=self.content_type, **kwargs)