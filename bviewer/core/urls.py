# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^$', 'bviewer.core.views.ShowHome', name='core.home'),
    url(r'^about/$', 'bviewer.core.views.ShowAbout', name='core.about'),
    url(r'^gallery/(?P<id>[\w]+)/$', 'bviewer.core.views.ShowGallery', name='core.gallery'),
    url(r'^image/(?P<id>\w+)/$', 'bviewer.core.views.ShowImage', name='core.image'),
    url(r'^video/(?P<id>\w+)/$', 'bviewer.core.views.ShowVideo', name='core.video'),
    url(r'^video/(?P<id>\w+)/thumbnail/$', 'bviewer.core.views.DownloadVideoThumbnail', name='core.video.thumbnail'),
    url(r'^download/(?P<size>\w+)/(?P<id>\w+).jpg$', 'bviewer.core.views.DownloadImage', name='core.download'),
)