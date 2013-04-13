# -*- coding: utf-8 -*-

from django.db.models import Q
from tastypie.authorization import Authorization

from bviewer.core.models import Gallery


class BaseAuthorization(Authorization):
    def read_detail(self, object_list, bundle):
        return len(self.read_list(object_list, bundle)) > 0


class GalleryAuthorization(BaseAuthorization):
    def read_list(self, object_list, bundle):
        user = bundle.request.user
        if user.is_authenticated():
            object_list = object_list.filter(Q(visibility=Gallery.VISIBLE) | Q(user=user))
        else:
            object_list = object_list.filter(visibility=Gallery.VISIBLE)
        return object_list


class GalleryItemAuthorization(BaseAuthorization):
    def read_list(self, object_list, bundle):
        user = bundle.request.user
        if user.is_authenticated():
            object_list = object_list.filter(Q(gallery__visibility=Gallery.VISIBLE) | Q(gallery__user=user))
        else:
            object_list = object_list.filter(gallery__visibility=Gallery.VISIBLE)
        return object_list