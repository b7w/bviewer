# -*- coding: utf-8 -*-
from django.conf.urls import url

from bviewer.slideshow import views

urlpatterns = [
    url(r'^$', views.index_view, name='slideshow.index'),
    url(r'^(?P<album_id>[\w]+)/$', views.album_view, name='slideshow.album'),
]
