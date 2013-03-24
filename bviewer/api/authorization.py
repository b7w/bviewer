# -*- coding: utf-8 -*-

from django.db.models import Q
from tastypie.authorization import Authorization


class BaseAuthorization(Authorization):
    def read_detail(self, object_list, bundle):
        return len(self.read_list(object_list, bundle)) > 0


class GalleryAuthorization(BaseAuthorization):
    def read_list(self, object_list, bundle):
        user = bundle.request.user
        if user.is_authenticated():
            object_list = object_list.filter(Q(private=False) | Q(user=user, private=True))
        else:
            object_list = object_list.filter(private=False)
        return object_list


class GalleryItemAuthorization(BaseAuthorization):
    def read_list(self, object_list, bundle):
        user = bundle.request.user
        if user.is_authenticated():
            object_list = object_list.filter(Q(gallery__private=False) | Q(gallery__user=user, gallery__private=True))
        else:
            object_list = object_list.filter(gallery__private=False)
        return object_list