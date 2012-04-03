# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns( '',
    url( r'^gallery/tree/main/$', 'bviewer.api.views.gallery.JsonGalleryTree', name='api.gallery.tree.main' ),
    url( r'^gallery/get/$', 'bviewer.api.views.gallery.JsonGalleryGet', name='api.gallery.get' ),
    url( r'^gallery/all/$', 'bviewer.api.views.gallery.JsonGalleryAll', name='api.gallery.all' ),
    url( r'^gallery/add/$', 'bviewer.api.views.gallery.JsonGalleryAdd', name='api.gallery.add' ),
    url( r'^gallery/update/$', 'bviewer.api.views.gallery.JsonGalleryUpdate', name='api.gallery.update' ),
    url( r'^gallery/child/add/$', 'bviewer.api.views.gallery.JsonGalleryChild', {'action': 'add'}, name='api.gallery.child.add' ),
    url( r'^gallery/child/del/$', 'bviewer.api.views.gallery.JsonGalleryChild', {'action': 'del'}, name='api.gallery.child.del' ),
    url( r'^gallery/del/$', 'bviewer.api.views.gallery.JsonGalleryRemove', name='api.gallery.remove' ),
    url( r'^gallery/cache/$', 'bviewer.api.views.gallery.JsonGalleryPreCache', name='api.gallery.precache' ),

    url( r'^images/get/$', 'bviewer.api.views.image.JsonImagesGet', name='api.image.get' ),
    url( r'^images/add/$', 'bviewer.api.views.image.JsonImageAdd', name='api.image.add' ),
    url( r'^images/del/$', 'bviewer.api.views.image.JsonImageRemove', name='api.image.del' ),

    url( r'^video/get/$', 'bviewer.api.views.videos.JsonVideoGet', name='api.video.get' ),
    url( r'^video/add/$', 'bviewer.api.views.videos.JsonVideoAdd', name='api.video.add' ),
    url( r'^video/del/$', 'bviewer.api.views.videos.JsonVideoRemove', name='api.video.del' ),
    url( r'^video/update/$', 'bviewer.api.views.videos.JsonVideoUpdate', name='api.video.update' ),

    url( r'^users/get/$', 'bviewer.api.views.users.JsonUserGet', name='api.user.get' ),
    url( r'^users/update/$', 'bviewer.api.views.users.JsonUserUpdate', name='api.user.update' ),

    url( r'^storage/list/$', 'bviewer.api.views.storage.JsonStorageList', name='api.storage.list' ),
)