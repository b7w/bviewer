# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^gallery/(?P<id>[\w]+)/archive/$', 'bviewer.archive.views.Archive', name='archive.archive'),
    url(r'^gallery/(?P<id>[\w]+)/archive/(?P<hash>[\w]+)/download/$', 'bviewer.archive.views.Download', name='archive.download'),
    url(r'^gallery/(?P<id>[\w]+)/archive/(?P<hash>[\w]+)/status/$', 'bviewer.archive.views.ArchiveStatus', name='archive.status'),
)
