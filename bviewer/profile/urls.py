# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url, include
from bviewer.profile.admin import profile


urlpatterns = patterns('bviewer.profile.views',
    url(r'^gallery/(?P<gallery_id>\w+)/album/(?P<album_id>\w+)/$',
        'images_view', name='profile.album'),
    url(r'^gallery/(?P<gallery_id>\w+)/album/(?P<album_id>\w+)/pre-cache/$',
        'album_pre_cache', name='profile.album.pre-cache'),
    url(r'^gallery/(?P<gallery_id>\w+)/image/download/$', 'download_image', name='profile.download'),
    url(r'^', include(profile.urls)),
)