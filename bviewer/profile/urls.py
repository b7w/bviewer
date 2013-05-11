# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url, include
from bviewer.profile.admin import profile


urlpatterns = patterns('',
    url(r'^gallery/(?P<uid>\w+)/$', 'bviewer.profile.views.images_view', name='profile.gallery'),
    url(r'^download/$', 'bviewer.profile.views.download_image', name='profile.download'),
    url(r'^', include(profile.urls)),
)