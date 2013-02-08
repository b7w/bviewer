# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^$', 'bviewer.profile.views.ShowHome', name='profile.home'),
    url(r'^galleries/$', 'bviewer.profile.views.ShowGalleries', name='profile.galleries'),
    url(r'^gallery/action/(?P<action>\w+)/$', 'bviewer.profile.views.GalleryAction', name='profile.gallery.action'),
    url(r'^images/$', 'bviewer.profile.views.ShowImages', name='profile.images'),
    url(r'^images2/$', 'bviewer.profile.views.ShowImagesAdmin', name='profile.images2'),
    url(r'^storage/$', 'bviewer.profile.views.JsonStorageList', name='profile.storage'),
    url(r'^videos/$', 'bviewer.profile.views.ShowVideos', name='profile.videos'),
    url(r'^about/$', 'bviewer.profile.views.ShowAbout', name='profile.about'),
    url(r'^image/$', 'bviewer.profile.views.DownloadImage', name='profile.image'),
)