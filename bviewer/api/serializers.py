# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from rest_framework.relations import HyperlinkedRelatedField, HyperlinkedIdentityField
from rest_framework.serializers import ModelSerializer

from bviewer.core.models import Album, Image, Video


class UserSerializer(ModelSerializer):
    detail = HyperlinkedIdentityField(view_name='proxyuser-detail')

    class Meta:
        model = User
        fields = ('detail', 'id', 'username', 'date_joined', 'last_login', 'about_title', 'about_text',)


class AlbumSerializer(ModelSerializer):
    detail = HyperlinkedIdentityField(view_name='album-detail')
    user_detail = HyperlinkedRelatedField(source='user', view_name='proxyuser-detail', read_only=True)
    parent_detail = HyperlinkedRelatedField(source='parent', view_name='album-detail', read_only=True)
    thumbnail_detail = HyperlinkedRelatedField(source='thumbnail', view_name='image-detail', read_only=True)

    class Meta:
        model = Album
        exclude = ('visibility', )


class ImageSerializer(ModelSerializer):
    detail = HyperlinkedIdentityField(view_name='image-detail')
    album_detail = HyperlinkedRelatedField(source='album', view_name='album-detail', read_only=True)

    def __init__(self, *args, **kwargs):
        super(ImageSerializer, self).__init__(*args, **kwargs)

    def to_native(self, obj):
        if obj and isinstance(obj, self.Meta.model):
            user = self.context['request'].user
            if not (user.is_authenticated() and obj.album.user_id == user.id):
                obj.path = None
        return super(ImageSerializer, self).to_native(obj)

    class Meta:
        model = Image


class VideoSerializer(ModelSerializer):
    detail = HyperlinkedIdentityField(view_name='video-detail')
    album_detail = HyperlinkedRelatedField(source='album', view_name='album-detail', read_only=True)

    class Meta:
        model = Video