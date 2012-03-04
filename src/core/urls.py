# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns( '',
    url( r'^$', 'django.views.generic.simple.redirect_to', {'url': '/user/'} ),
    url( r'^user/(?P<user>\w*)/?about/$', 'core.views.ShowAbout', name='core.about' ),
    url( r'^user/(?P<user>\w*)/?$', 'core.views.ShowHome', name='core.home' ),
    url( r'^user/(?P<user>\w*)/?gallery/(?P<id>[\w.]+)/$', 'core.views.ShowGallery', name='core.gallery' ),
    url( r'^user/(?P<user>\w*)/?image/(?P<id>\w+)/$', 'core.views.ShowImage', name='core.image' ),
    url( r'^user/(?P<user>\w*)/?video/(?P<id>\w+)/$', 'core.views.ShowVideo', name='core.video' ),
    url( r'^user/(?P<user>\w*)/?video/(?P<id>\w+)/thumbnail/$', 'core.views.DownloadVideoThumbnail', name='core.video.thumbnail' ),
    url( r'^user/(?P<user>\w*)/?download/(?P<size>\w+)/(?P<id>\w+).jpg$', 'core.views.DownloadImage', name='core.download' ),

)