# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from rest_framework.relations import HyperlinkedRelatedField, HyperlinkedIdentityField
from rest_framework.serializers import ModelSerializer

from bviewer.core.models import Gallery, Album, Image, Video


class UserSerializer(ModelSerializer):
    detail = HyperlinkedIdentityField(view_name='user-detail')

    class Meta:
        model = User
        fields = ('detail', 'id', 'username', 'date_joined', 'last_login', )


class GallerySerializer(ModelSerializer):
    detail = HyperlinkedIdentityField(view_name='gallery-detail')
    user_detail = HyperlinkedRelatedField(source='user', view_name='user-detail', read_only=True)

    class Meta:
        model = Gallery


class AlbumSerializer(ModelSerializer):
    detail = HyperlinkedIdentityField(view_name='album-detail')
    gallery_detail = HyperlinkedRelatedField(source='gallery', view_name='gallery-detail', read_only=True)
    parent_detail = HyperlinkedRelatedField(source='parent', view_name='album-detail', read_only=True)
    thumbnail_detail = HyperlinkedRelatedField(source='thumbnail', view_name='image-detail', read_only=True)

    class Meta:
        model = Album
        exclude = ('visibility', )


class ImageSerializer(ModelSerializer):
    detail = HyperlinkedIdentityField(view_name='image-detail')
    album_detail = HyperlinkedRelatedField(source='album', view_name='album-detail', read_only=True)

    def to_native(self, obj):
        if obj and isinstance(obj, self.Meta.model):
            user = self.context['request'].user
            if not (user.is_authenticated() and obj.album.gallery.user_id == user.id):
                obj.path = None
        return super(ImageSerializer, self).to_native(obj)

    class Meta:
        model = Image


class VideoSerializer(ModelSerializer):
    detail = HyperlinkedIdentityField(view_name='video-detail')
    album_detail = HyperlinkedRelatedField(source='album', view_name='album-detail', read_only=True)

    class Meta:
        model = Video