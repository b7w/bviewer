# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url, include
from bviewer.profile.admin import profile


urlpatterns = patterns('bviewer.profile.views',
    url(r'^album/(?P<uid>\w+)/$', 'images_view', name='profile.album'),
    url(r'^album/(?P<uid>\w+)/pre-cache/$', 'album_pre_cache', name='profile.album.pre-cache'),
    url(r'^download/$', 'download_image', name='profile.download'),
    url(r'^', include(profile.urls)),
)