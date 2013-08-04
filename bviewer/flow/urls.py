# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^flow/(?P<uid>[\w]+)/$', 'bviewer.flow.views.gallery_view', name='flow.gallery'),
    url(r'^flow/(?P<uid>[\w]+)/images/$', 'bviewer.flow.views.flow_view', name='flow.flow'),
)