# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns( '',
    url( r'^gallery/tree/main/$', 'api.views.gallery.JsonGalleryTree', name='api.gallery.tree.main' ),
    url( r'^gallery/get/$', 'api.views.gallery.JsonGalleryGet', name='api.gallery.get' ),
    url( r'^gallery/all/$', 'api.views.gallery.JsonGalleryAll', name='api.gallery.all' ),
    url( r'^gallery/add/$', 'api.views.gallery.JsonGalleryAdd', name='api.gallery.add' ),
    url( r'^gallery/update/$', 'api.views.gallery.JsonGalleryUpdate', name='api.gallery.update' ),
    url( r'^gallery/child/add/$', 'api.views.gallery.JsonGalleryChild', {'action': 'add'}, name='api.gallery.child.add' ),
    url( r'^gallery/child/del/$', 'api.views.gallery.JsonGalleryChild', {'action': 'del'}, name='api.gallery.child.del' ),
    url( r'^gallery/del/$', 'api.views.gallery.JsonGalleryRemove', name='api.gallery.remove' ),
    url( r'^gallery/cache/$', 'api.views.gallery.JsonGalleryPreCache', name='api.gallery.precache' ),

    url( r'^images/get/$', 'api.views.image.JsonImagesGet', name='api.image.get' ),
    url( r'^images/add/$', 'api.views.image.JsonImageAdd', name='api.image.add' ),
    url( r'^images/del/$', 'api.views.image.JsonImageRemove', name='api.image.del' ),

    url( r'^video/get/$', 'api.views.videos.JsonVideoGet', name='api.video.get' ),
    url( r'^video/add/$', 'api.views.videos.JsonVideoAdd', name='api.video.add' ),
    url( r'^video/del/$', 'api.views.videos.JsonVideoRemove', name='api.video.del' ),
    url( r'^video/update/$', 'api.views.videos.JsonVideoUpdate', name='api.video.update' ),

    url( r'^users/get/$', 'api.views.users.JsonUserGet', name='api.user.get' ),
    url( r'^users/update/$', 'api.views.users.JsonUserUpdate', name='api.user.update' ),

    url( r'^storage/list/$', 'api.views.storage.JsonStorageList', name='api.storage.list' ),
)