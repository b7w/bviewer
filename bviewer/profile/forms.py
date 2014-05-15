# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from bviewer.core.models import Gallery, Video


class AdminGalleryForm(ModelForm):
    def clean_title(self):
        title = self.cleaned_data['title']
        user_id = self.data['user']
        if Gallery.objects.filter(title=title, user_id=user_id).exclude(id=self.instance.id).count() > 0:
            raise ValidationError('Title must be unique')
        return title

    class Meta(object):
        model = Gallery


class GalleryForm(ModelForm):
    class Meta(object):
        model = Gallery
        fields = ('title', 'visibility', 'description', 'time')


class VideoForm(ModelForm):
    class Meta(object):
        model = Video
        fields = ('uid', 'type', 'title', 'description')