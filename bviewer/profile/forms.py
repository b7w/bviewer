# -*- coding: utf-8 -*-

from django.forms import ModelForm

from bviewer.core.models import Gallery, Video


class GalleryForm(ModelForm):
    class Meta:
        model = Gallery
        fields = ('title', 'private', 'description', 'time')


class VideoForm(ModelForm):
    class Meta:
        model = Video
        fields = ('uid', 'type', 'title', 'description')