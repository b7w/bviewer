# -*- coding: utf-8 -*-
from rest_framework.filters import BaseFilterBackend


class GalleryUserSelfFilter(BaseFilterBackend):
    HTTP_METHODS = ('POST', 'DELETE',)
    GET_PARAM = 'user__self'
    QUERYSET_PARAM = 'user'

    def filter_queryset(self, request, queryset, view):
        if request.user.is_authenticated():
            if self.GET_PARAM in request.GET or request.method in self.HTTP_METHODS:
                kwargs = {self.QUERYSET_PARAM: request.user}
                return queryset.filter(**kwargs)
        return queryset


class AlbumUserSelfFilter(GalleryUserSelfFilter):
    QUERYSET_PARAM = 'gallery__user'


class ItemUserSelfFilter(GalleryUserSelfFilter):
    QUERYSET_PARAM = 'album__gallery__user'
