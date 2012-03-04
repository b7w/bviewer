# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns( '',
    url( r'^$', 'profile.views.ShowHome', name='profile.home' ),
    url( r'^galleries/$', 'profile.views.ShowGalleries', name='profile.galleries' ),
    url( r'^images/$', 'profile.views.ShowImages', name='profile.images' ),
    url( r'^videos/$', 'profile.views.ShowVideos', name='profile.videos' ),
    url( r'^about/$', 'profile.views.ShowAbout', name='profile.about' ),
    url( r'^image/$', 'profile.views.DownloadImage', name='profile.image' ),
)