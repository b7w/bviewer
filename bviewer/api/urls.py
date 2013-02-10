# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url, include

from bviewer.api.versions import version1

urlpatterns = patterns('',
    url(r'^', include(version1.urls), name='api.v1'),
)