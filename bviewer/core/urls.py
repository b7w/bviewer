# -*- coding: utf-8 -*-

from django.conf.urls import url

from bviewer.core import views

urlpatterns = [
    url(r'^$', views.index_view, name='core.home'),
    url(r'^about/$', views.about_view, name='core.about'),
    url(r'^login/$', views.login_view, name='core.login'),
    url(r'^request/registration/$', views.registration_view, name='core.registration'),
    url(r'^logout/$', views.logout_view, name='core.logout'),
    url(r'^album/(?P<uid>[\w]+)/$', views.album_view, name='core.album'),
    url(r'^image/(?P<uid>\w+)/$', views.image_view, name='core.image'),
    url(r'^video/(?P<uid>\w+)/$', views.video_view, name='core.video'),
    url(r'^video/(?P<uid>\w+)/url/$', views.video_redirect_view, name='core.video.url'),
    url(r'^video/(?P<uid>\w+)/thumbnail/$', views.download_video_thumbnail_view, name='core.video.thumbnail'),
    url(r'^download/(?P<size>\w+)/(?P<uid>\w+).jpg$', views.download_image_view, name='core.download'),
]
