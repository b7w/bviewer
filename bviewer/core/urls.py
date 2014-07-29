# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('bviewer.core.views',
    url(r'^$', 'index_view', name='core.home'),
    url(r'^about/$', 'about_view', name='core.about'),
    url(r'^login/$', 'login_view', name='core.login'),
    url(r'^request/registration/$', 'registration_view', name='core.registration'),
    url(r'^logout/$', 'logout_view', name='core.logout'),
    url(r'^album/(?P<uid>[\w]+)/$', 'album_view', name='core.album'),
    url(r'^image/(?P<uid>\w+)/$', 'image_view', name='core.image'),
    url(r'^video/(?P<uid>\w+)/$', 'video_view', name='core.video'),
    url(r'^video/(?P<uid>\w+)/thumbnail/$', 'download_video_thumbnail_view', name='core.video.thumbnail'),
    url(r'^download/(?P<size>\w+)/(?P<uid>\w+).jpg$', 'download_image_view', name='core.download'),
)