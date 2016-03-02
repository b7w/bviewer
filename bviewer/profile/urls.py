# -*- coding: utf-8 -*-

from django.conf.urls import url, include

from bviewer.profile import views
from bviewer.profile.admin import profile

urlpatterns = [
    url(r'^gallery/(?P<gallery_id>\w+)/album/(?P<album_id>\w+)/$',
        views.images_view, name='profile.album'),
    url(r'^gallery/(?P<gallery_id>\w+)/album/(?P<album_id>\w+)/pre-cache/$',
        views.album_pre_cache, name='profile.album.pre-cache'),
    url(r'^gallery/(?P<gallery_id>\w+)/image/download/$', views.download_image, name='profile.download'),
    url(r'^', include(profile.urls)),
]
