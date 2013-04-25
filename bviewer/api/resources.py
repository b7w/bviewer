# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse

from tastypie import fields
from tastypie.authentication import Authentication, MultiAuthentication, SessionAuthentication
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.resources import ModelResource

from bviewer.api.authorization import GalleryAuthorization, GalleryItemAuthorization
from bviewer.core import settings
from bviewer.core.models import Gallery, ProxyUser, Image, Video

EXACT = ['exact', ]


class UserResource(ModelResource):
    class Meta:
        queryset = ProxyUser.objects.all()
        resource_name = 'user'
        allowed_methods = ['get', ]
        excludes = ['email', 'password', 'is_active', 'is_staff', 'is_superuser', ]
        filtering = {
            'id': EXACT,
            'username': ALL,
        }


class GalleryResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user')

    def dehydrate(self, bundle):
        bundle.data['id'] = bundle.obj.id  # make ID integer
        bundle.data['user_id'] = bundle.obj.user_id
        bundle.data['parent_id'] = bundle.obj.parent_id
        return bundle

    def apply_filters(self, request, filters):
        """
        If filter `user=self` and is authenticated, replace it with his id
        """
        query = 'user__exact'
        if query in filters and filters[query] == 'self' and request.user.is_authenticated():
            filters[query] = request.user.id
        return super(GalleryResource, self).apply_filters(request, filters)

    class Meta:
        queryset = Gallery.objects.all().select_related()
        resource_name = 'gallery'
        allowed_methods = ['get', ]
        excludes = ['visibility', ]
        authentication = MultiAuthentication(SessionAuthentication(), Authentication())
        authorization = GalleryAuthorization()
        filtering = {
            'id': EXACT,
            'user': ALL_WITH_RELATIONS,
            'title': ALL,
            'visibility': EXACT,
            'time': ALL,
        }


class GalleryItemResource(ModelResource):
    """
    Abstract class for Models that have Gallery FK.
    Need to implement Meta.queryset.
    """

    gallery = fields.ForeignKey(GalleryResource, 'gallery')

    def dehydrate(self, bundle):
        bundle.data['id'] = bundle.obj.id  # make ID integer
        bundle.data['gallery_id'] = bundle.obj.gallery_id
        return bundle

    def apply_filters(self, request, filters):
        """
        If filter `gallery__user=self` and is authenticated, replace it with his id
        """
        query = 'gallery__user__exact'
        if query in filters and filters[query] == 'self' and request.user.is_authenticated():
            filters[query] = request.user.id
        return super(GalleryItemResource, self).apply_filters(request, filters)

    class Meta:
        allowed_methods = ['get', ]
        authentication = MultiAuthentication(SessionAuthentication(), Authentication())
        authorization = GalleryItemAuthorization()
        filtering = {
            'id': EXACT,
            'gallery': ALL_WITH_RELATIONS,
        }


class ImageResource(GalleryItemResource):
    def dehydrate(self, bundle):
        """
        Add links to images. Show path field only for owner.
        """
        obj_id = bundle.obj.id
        bundle.data['url'] = reverse('core.image', kwargs=dict(uid=obj_id))
        links = {}
        for size in settings.VIEWER_IMAGE_SIZE:
            links[size] = reverse('core.download', kwargs=dict(size=size, uid=obj_id))
        bundle.data['image'] = links

        user = bundle.request.user
        if not (user.is_authenticated() and user.id == bundle.obj.gallery.user_id):
            del bundle.data['path']
        return super(ImageResource, self).dehydrate(bundle)

    class Meta(GalleryItemResource.Meta):
        queryset = Image.objects.all().select_related()
        resource_name = 'image'
        filtering = dict(
            path=ALL,
            **GalleryItemResource.Meta.filtering
        )


class VideoResource(GalleryItemResource):
    def dehydrate(self, bundle):
        """
        Add links to videos
        """
        obj_id = bundle.obj.id
        bundle.data['url'] = reverse('core.video', kwargs=dict(uid=obj_id))
        bundle.data['thumbnail'] = reverse('core.video.thumbnail', kwargs=dict(uid=obj_id))
        return super(VideoResource, self).dehydrate(bundle)

    class Meta(GalleryItemResource.Meta):
        queryset = Video.objects.all().select_related()
        resource_name = 'video'
        filtering = dict(
            uid=EXACT,
            type=ALL,
            title=ALL,
            **GalleryItemResource.Meta.filtering
        )