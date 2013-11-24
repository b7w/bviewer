# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

urlpatterns = patterns('bviewer.slideshow.views',
    url(r'^(?P<gallery_id>[\w]+)/$', 'index_view', name='slideshow.index'),
)
