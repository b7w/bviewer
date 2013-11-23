# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

urlpatterns = patterns('bviewer.slideshow.views',
    url(r'^$', 'index_view', name='slideshow.index'),
    url(r'^next/$', 'next_image_view', name='slideshow.next'),
)
