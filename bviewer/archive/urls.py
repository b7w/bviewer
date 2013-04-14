# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^archive/(?P<id>[\w]+)/$', 'bviewer.archive.views.Archive', name='archive.archive'),
    url(r'^archive/(?P<id>[\w]+)/(?P<hash>[\w]+)/download/$', 'bviewer.archive.views.Download', name='archive.download'),
    url(r'^archive/(?P<id>[\w]+)/(?P<hash>[\w]+)/status/$', 'bviewer.archive.views.ArchiveStatus', name='archive.status'),
)
