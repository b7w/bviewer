# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^$', 'bviewer.core.views.index_view', name='core.home'),
    url(r'^about/$', 'bviewer.core.views.about_view', name='core.about'),
    url(r'^gallery/(?P<uid>[\w]+)/$', 'bviewer.core.views.gallery_view', name='core.gallery'),
    url(r'^image/(?P<uid>\w+)/$', 'bviewer.core.views.image_view', name='core.image'),
    url(r'^video/(?P<uid>\w+)/$', 'bviewer.core.views.video_view', name='core.video'),
    url(r'^video/(?P<uid>\w+)/thumbnail/$', 'bviewer.core.views.download_video_thumbnail_view', name='core.video.thumbnail'),
    url(r'^download/(?P<size>\w+)/(?P<uid>\w+).jpg$', 'bviewer.core.views.download_image_view', name='core.download'),
)