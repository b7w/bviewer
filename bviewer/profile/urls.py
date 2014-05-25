# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url, include
from bviewer.profile.admin import profile


urlpatterns = patterns('bviewer.profile.views',
    url(r'^gallery/(?P<uid>\w+)/$', 'images_view', name='profile.gallery'),
    url(r'^gallery/(?P<uid>\w+)/pre-cache/$', 'gallery_pre_cache', name='profile.gallery.pre-cache'),
    url(r'^download/$', 'download_image', name='profile.download'),
    url(r'^', include(profile.urls)),
)