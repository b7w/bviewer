# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    url(r'^', include('bviewer.core.urls')),
    url(r'^archive/', include('bviewer.archive.urls')),
    url(r'^api/', include('bviewer.api.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^profile/', include('bviewer.profile.urls')),
    url(r'^slideshow/', include('bviewer.slideshow.urls')),
    url(r'^rq/', include('django_rq.urls')),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                      url(r'^__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns
