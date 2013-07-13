# -*- coding: utf-8 -*-

from django.forms import ModelForm

from bviewer.core.models import Gallery, Video


class GalleryForm(ModelForm):
    class Meta(object):
        model = Gallery
        fields = ('title', 'visibility', 'description', 'time')


class VideoForm(ModelForm):
    class Meta(object):
        model = Video
        fields = ('uid', 'type', 'title', 'description')