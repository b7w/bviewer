# -*- coding: utf-8 -*-
from django.db.models import Q

from rest_framework.filters import OrderingFilter, DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet
from bviewer.api.filters import UserSelfFilter, ItemUserSelfFilter

from bviewer.api.serializers import UserSerializer, GallerySerializer, ImageSerializer, VideoSerializer
from bviewer.core.models import Gallery, ProxyUser, Image, Video


ITEMS_PER_PAGE = 16


class UserResource(ModelViewSet):
    queryset = ProxyUser.objects.all().select_related()
    serializer_class = UserSerializer
    http_method_names = ('get',)
    permission_classes = (IsAuthenticated,)

    filter_backends = (OrderingFilter, DjangoFilterBackend,)
    filter_fields = ('id', 'username')
    ordering = ('username',)

    paginate_by = ITEMS_PER_PAGE


class GalleryResource(ModelViewSet):
    queryset = Gallery.objects.all().select_related()

    http_method_names = ('get', 'post', 'delete',)
    serializer_class = GallerySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    filter_backends = (UserSelfFilter, OrderingFilter, DjangoFilterBackend)
    filter_fields = ('id', 'user', 'title')
    ordering = ('title', 'time',)

    paginate_by = ITEMS_PER_PAGE

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated():
            return self.queryset.filter(Q(visibility=Gallery.VISIBLE) | Q(user=user))
        else:
            return self.queryset.filter(visibility=Gallery.VISIBLE)


class ImageResource(ModelViewSet):
    queryset = Image.objects.all().select_related()

    http_method_names = ('get', 'post', 'delete',)
    serializer_class = ImageSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )

    filter_backends = (ItemUserSelfFilter, OrderingFilter, DjangoFilterBackend,)
    filter_fields = ('id', 'gallery', 'path', )
    ordering = ('time',)

    paginate_by = ITEMS_PER_PAGE

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated():
            return self.queryset.filter(Q(gallery__visibility=Gallery.VISIBLE) | Q(gallery__user=user))
        else:
            return self.queryset.filter(gallery__visibility=Gallery.VISIBLE)


class VideoResource(ModelViewSet):
    queryset = Video.objects.all().select_related()

    http_method_names = ('get', 'post', 'delete',)
    serializer_class = VideoSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )

    filter_backends = (ItemUserSelfFilter, OrderingFilter, DjangoFilterBackend,)
    filter_fields = ('id', 'gallery',)
    ordering = ('time',)

    paginate_by = ITEMS_PER_PAGE

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated():
            return self.queryset.filter(Q(gallery__visibility=Gallery.VISIBLE) | Q(gallery__user=user))
        else:
            return self.queryset.filter(gallery__visibility=Gallery.VISIBLE)