# -*- coding: utf-8 -*-

from django.conf.urls import url

from bviewer.archive import views

urlpatterns = [
    url(r'^(?P<gid>[\w]+)/$', views.index_view, name='archive.archive'),
    url(r'^(?P<gid>[\w]+)/(?P<uid>[\w]+)/download/$', views.download_view, name='archive.download'),
    url(r'^(?P<gid>[\w]+)/(?P<uid>[\w]+)/status/$', views.status_view, name='archive.status'),
]
