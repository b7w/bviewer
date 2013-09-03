# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('bviewer.core.views',
    url(r'^$', 'index_view', name='core.home'),
    url(r'^about/$', 'about_view', name='core.about'),
    url(r'^login/$', 'login_view', name='core.login'),
    url(r'^logout/$', 'logout_view', name='core.logout'),
    url(r'^gallery/(?P<uid>[\w]+)/$', 'gallery_view', name='core.gallery'),
    url(r'^image/(?P<uid>\w+)/$', 'image_view', name='core.image'),
    url(r'^video/(?P<uid>\w+)/$', 'video_view', name='core.video'),
    url(r'^video/(?P<uid>\w+)/thumbnail/$', 'download_video_thumbnail_view', name='core.video.thumbnail'),
    url(r'^download/(?P<size>\w+)/(?P<uid>\w+).jpg$', 'download_image_view', name='core.download'),
)