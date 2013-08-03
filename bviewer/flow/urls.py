# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^flow/(?P<uid>[\w]+)/row/$', 'bviewer.flow.views.gallery_view', name='flow.gallery'),
    url(r'^flow/(?P<uid>[\w]+)/row/flow/$', 'bviewer.flow.views.flow_view', name='flow.flow'),
)