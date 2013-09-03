# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('bviewer.archive.views',
    url(r'^(?P<gid>[\w]+)/$', 'index_view', name='archive.archive'),
    url(r'^(?P<gid>[\w]+)/(?P<uid>[\w]+)/download/$', 'download_view', name='archive.download'),
    url(r'^(?P<gid>[\w]+)/(?P<uid>[\w]+)/status/$', 'status_view', name='archive.status'),
)
