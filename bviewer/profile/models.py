# -*- coding: utf-8 -*-

from bviewer.core.models import ProxyUser, Gallery, Image, Video

# TODO: fix `app_label = 'core'`
# It is hack to show proxy models for not super users


class ProfileProxyUser(ProxyUser):
    class Meta:
        proxy = True
        app_label = 'core'
        verbose_name = 'Profile User'


class ProfileGallery(Gallery):
    class Meta:
        proxy = True
        app_label = 'core'
        verbose_name = 'Profile Gallery'
        verbose_name_plural = 'Profile Galleries'


class ProfileImage(Image):
    class Meta:
        proxy = True
        app_label = 'core'
        verbose_name = 'Profile Image'


class ProfileVideo(Video):
    class Meta:
        proxy = True
        app_label = 'core'
        verbose_name = 'Profile Video'
