# -*- coding: utf-8 -*-
from rest_framework.relations import HyperlinkedRelatedField
from rest_framework.serializers import ModelSerializer

from bviewer.core.models import ProxyUser, Gallery, Image, Video


class UserSerializer(ModelSerializer):
    class Meta:
        model = ProxyUser
        exclude = ('email', 'password', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions',)


class GallerySerializer(ModelSerializer):
    user_detail = HyperlinkedRelatedField(source='user', view_name='proxyuser-detail', read_only=True)
    parent_detail = HyperlinkedRelatedField(source='parent', view_name='gallery-detail', read_only=True)
    thumbnail_detail = HyperlinkedRelatedField(source='thumbnail', view_name='image-detail', read_only=True)

    class Meta:
        model = Gallery
        exclude = ('visibility', )


class ImageSerializer(ModelSerializer):
    gallery_detail = HyperlinkedRelatedField(source='gallery', view_name='gallery-detail', read_only=True)

    def __init__(self, *args, **kwargs):
        super(ImageSerializer, self).__init__(*args, **kwargs)

    def to_native(self, obj):
        if obj and isinstance(obj, self.Meta.model):
            user = self.context['request'].user
            if not (user.is_authenticated() and obj.gallery.user_id == user.id):
                obj.path = None
        return super(ImageSerializer, self).to_native(obj)

    class Meta:
        model = Image


class VideoSerializer(ModelSerializer):
    gallery_detail = HyperlinkedRelatedField(source='gallery', view_name='gallery-detail', read_only=True)

    class Meta:
        model = Video