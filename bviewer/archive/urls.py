# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^archive/(?P<gid>[\w]+)/$', 'bviewer.archive.views.index_view', name='archive.archive'),
    url(r'^archive/(?P<gid>[\w]+)/(?P<uid>[\w]+)/download/$', 'bviewer.archive.views.download_view', name='archive.download'),
    url(r'^archive/(?P<gid>[\w]+)/(?P<uid>[\w]+)/status/$', 'bviewer.archive.views.status_view', name='archive.status'),
)
