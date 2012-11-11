# -*- coding: utf-8 -*-

from django.forms import ModelForm

from bviewer.core.models import Gallery


class GalleryForm(ModelForm):
    class Meta:
        model = Gallery
        fields = ('title', 'private', 'description', 'time')