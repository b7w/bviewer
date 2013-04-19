# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url, include
from bviewer.profile.admin import profile


urlpatterns = patterns('',
    url(r'^storage/$', 'bviewer.profile.views.json_storage_view', name='profile.storage'),
    url(r'^images/$', 'bviewer.profile.views.images_view', name='profile.images'),
    url(r'^images/update/$', 'bviewer.profile.views.json_image_view', name='profile.images.update'),
    url(r'^download/$', 'bviewer.profile.views.download_image', name='profile.download'),
    url(r'^', include(profile.urls)),
)