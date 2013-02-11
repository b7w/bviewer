# -*- coding: utf-8 -*-

from django.test.client import Client
from tastypie.serializers import Serializer


class ResourceClient(Client):
    content_type = 'application/json'

    def __init__(self, enforce_csrf_checks=False, **defaults):
        super(ResourceClient, self).__init__(enforce_csrf_checks, **defaults)
        self.serializer = Serializer()

    def read(self, path, data=None, **kwargs):
        kwargs['HTTP_ACCEPT'] = self.content_type
        if data is not None:
            kwargs['data'] = data

        response = self.get(path, **kwargs)
        result = self.serializer.deserialize(response.content, format=self.content_type)
        response.meta = result['meta']
        response.objects = result['objects']
        return response
