# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^', include('bviewer.core.urls')),
    url(r'^', include('bviewer.archive.urls')),
    url(r'^api/', include('bviewer.api.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^profile/', include('bviewer.profile.urls')),
    url(r'^rq/', include('django_rq.urls')),
)
