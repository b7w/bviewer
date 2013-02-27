# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.db.models import Q
from tastypie import fields
from tastypie.authentication import Authentication, MultiAuthentication, SessionAuthentication
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.exceptions import Unauthorized
from tastypie.resources import ModelResource

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
    #parent = fields.ForeignKey('self', 'parent', null=True) # Generate parent select per each item

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

    def authorized_read_list(self, object_list, bundle):
        user = bundle.request.user
        if user.is_authenticated():
            object_list = object_list.filter(Q(private=False) | Q(user=user, private=True))
        else:
            object_list = object_list.filter(private=False)
        return object_list

    def authorized_read_detail(self, object_list, bundle):
        # TODO: WTF, https://github.com/toastdriven/django-tastypie/issues/826
        if len(self.authorized_read_list(object_list, bundle)) > 0:
            return True
        raise Unauthorized("You are not allowed to access that resource.")

    class Meta:
        queryset = Gallery.objects.all().select_related()
        resource_name = 'gallery'
        allowed_methods = ['get', ]
        excludes = ['private', ]
        authentication = MultiAuthentication(SessionAuthentication(), Authentication())
        filtering = {
            'id': EXACT,
            'user': ALL_WITH_RELATIONS,
            'title': ALL,
            'private': EXACT,
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

    def authorized_read_list(self, object_list, bundle):
        user = bundle.request.user
        if user.is_authenticated():
            object_list = object_list.filter(Q(gallery__private=False) | Q(gallery__user=user, gallery__private=True))
        else:
            object_list = object_list.filter(gallery__private=False)
        return object_list

    def authorized_read_detail(self, object_list, bundle):
        # TODO: WTF, https://github.com/toastdriven/django-tastypie/issues/826
        if len(self.authorized_read_list(object_list, bundle)) > 0:
            return True
        raise Unauthorized("You are not allowed to access that resource.")

    class Meta:
        allowed_methods = ['get', ]
        authentication = MultiAuthentication(SessionAuthentication(), Authentication())
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
        user_url = bundle.obj.gallery.user.url + '/'
        bundle.data['url'] = reverse('core.image', kwargs=dict(user=user_url, id=obj_id))
        for size in ['small', 'middle', 'big', 'full']:
            key = 'image_{0}'.format(size)
            bundle.data[key] = reverse('core.download', kwargs=dict(user=user_url, size=size, id=obj_id))

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
        user_url = bundle.obj.gallery.user.url + '/'
        bundle.data['url'] = reverse('core.video', kwargs=dict(user=user_url, id=obj_id))
        bundle.data['thumbnail'] = reverse('core.video.thumbnail', kwargs=dict(user=user_url, id=obj_id))
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