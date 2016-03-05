# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework.filters import OrderingFilter, DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet

from bviewer.api.common import StandardPagination
from bviewer.api.serializers import UserSerializer, GallerySerializer, AlbumSerializer, ImageSerializer, VideoSerializer
from bviewer.core.models import Gallery, Album, Image, Video


class UserResource(ModelViewSet):
    queryset = User.objects.all().select_related()
    serializer_class = UserSerializer
    http_method_names = ('get',)
    permission_classes = (IsAuthenticated,)

    filter_backends = (OrderingFilter, DjangoFilterBackend,)
    filter_fields = ('id', 'username')
    ordering = ('username',)

    pagination_class = StandardPagination


class GalleryResource(ModelViewSet):
    queryset = Gallery.objects.all().select_related()

    http_method_names = ('get', 'post', 'delete',)
    serializer_class = GallerySerializer
    permission_classes = (IsAuthenticated,)

    filter_backends = (OrderingFilter, DjangoFilterBackend,)
    ordering = ('user',)

    pagination_class = StandardPagination


class AlbumResource(ModelViewSet):
    queryset = Album.objects.all().select_related()

    http_method_names = ('get', 'post', 'delete',)
    serializer_class = AlbumSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filter_fields = ('id', 'gallery', 'title')
    ordering = ('title', 'time',)

    pagination_class = StandardPagination

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated():
            return self.queryset.filter(Q(visibility=Album.VISIBLE) | Q(gallery__user=user))
        else:
            return self.queryset.filter(visibility=Album.VISIBLE)


class ImageResource(ModelViewSet):
    queryset = Image.objects.all().select_related()

    http_method_names = ('get', 'post', 'delete',)
    serializer_class = ImageSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    filter_backends = (OrderingFilter, DjangoFilterBackend,)
    filter_fields = ('id', 'album', 'path',)
    ordering = ('time',)

    pagination_class = StandardPagination

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated():
            return self.queryset.filter(Q(album__visibility=Album.VISIBLE) | Q(album__gallery__user=user))
        else:
            return self.queryset.filter(album__visibility=Album.VISIBLE)


class VideoResource(ModelViewSet):
    queryset = Video.objects.all().select_related()

    http_method_names = ('get', 'post', 'delete',)
    serializer_class = VideoSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    filter_backends = (OrderingFilter, DjangoFilterBackend,)
    filter_fields = ('id', 'album',)
    ordering = ('time',)

    pagination_class = StandardPagination

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated():
            return self.queryset.filter(Q(album__visibility=Album.VISIBLE) | Q(album__gallery__user=user))
        else:
            return self.queryset.filter(album__visibility=Album.VISIBLE)
