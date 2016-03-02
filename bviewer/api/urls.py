# -*- coding: utf-8 -*-

from django.conf.urls import url, include

from bviewer.api.versions import version1

urlpatterns = [
    url(r'^v1/', include(version1.urls), name='api.v1'),
]
