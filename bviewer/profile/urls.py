# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^storage/$', 'bviewer.profile.views.JsonStorageList', name='profile.storage'),
    url(r'^images/$', 'bviewer.profile.views.ShowImagesAdmin', name='profile.images'),
    url(r'^images/update/$', 'bviewer.profile.views.JsonImageService', name='profile.images.update'),
    url(r'^download/$', 'bviewer.profile.views.DownloadImage', name='profile.download'),
)