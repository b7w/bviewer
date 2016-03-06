# -*- coding: utf-8 -*-
import re
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.forms import Form, ModelForm, ChoiceField, CharField, MultipleHiddenInput

from bviewer.core.models import Gallery, Album, Video


class BulkTimeUpdateForm(Form):
    ADD = 'add'
    SUBTRACT = 'subtract'
    CHOICES = (
        (ADD, 'Add'),
        (SUBTRACT, 'Subtract')
    )
    DIMENSIONS = ('days', 'seconds', 'minutes', 'hours', 'weeks')
    _selected_action = CharField(widget=MultipleHiddenInput)
    method = ChoiceField(choices=CHOICES)
    interval = CharField()

    def clean_interval(self):
        interval = self.cleaned_data['interval']
        dimensions_symbol = tuple(i[0] for i in self.DIMENSIONS)
        if not re.match(r'[\d{0}]'.format(''.join(dimensions_symbol)), interval):
            raise ValidationError('Wrong format, support only {0}'.format(self.DIMENSIONS))
        kwargs = {}
        for symbol, dimension in zip(dimensions_symbol, self.DIMENSIONS):
            match = re.search(r'\d+{0}'.format(symbol), interval)
            if match:
                kwargs[dimension] = int(match.group()[:-1])
        return timedelta(**kwargs)


class AdminGalleryForm(ModelForm):
    """
    Set for UserAdmin Gallery model except User.
    Add choice field for cache size filed.
    """

    def __init__(self, *args, **kwargs):
        super(AdminGalleryForm, self).__init__(*args, **kwargs)
        self._set_choice('cache_size', Gallery.CACHE_SIZE_MAX)
        self._set_choice('cache_archive_size', Gallery.CACHE_ARCHIVE_SIZE_MAX)

    def _set_choice(self, field_name, cache_max):
        base = cache_max // 8
        raising = (i * base for i in range(1, 9))
        choice = set([(i, '{0} MB'.format(i)) for i in raising])
        if self.instance:
            attr = getattr(self.instance, field_name)
            choice.add((attr, '{0} MB'.format(attr)))
        self.fields[field_name] = ChoiceField(choices=sorted(choice))

    class Meta(object):
        model = Gallery
        fields = '__all__'


class AdminAlbumForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(AdminAlbumForm, self).__init__(*args, **kwargs)
        if self.instance.gallery_id:
            self.fields['parent'].queryset = Album.objects \
                .filter(gallery__user=self.instance.gallery.user, gallery=self.instance.gallery)

    def clean_gallery(self):
        gallery = self.cleaned_data['gallery']
        if self.instance.gallery_id and self.instance.id == self.instance.gallery.top_album_id \
                and self.instance.gallery_id != gallery.id:
            raise ValidationError('You can not change gallery top album')
        return gallery

    def clean_parent(self):
        gallery = self.cleaned_data.get('gallery')
        album = self.cleaned_data['parent']
        if 'gallery' in self.changed_data:
            return None
        if gallery and album and album.gallery != gallery:
            raise ValidationError('Album must be from {0} gallery'.format(gallery))
        return album

    class Meta(object):
        model = Album
        fields = '__all__'


class AlbumForm(ModelForm):
    class Meta(object):
        model = Album
        fields = ('title', 'visibility', 'description', 'time')


class VideoForm(ModelForm):
    class Meta(object):
        model = Video
        fields = ('uid', 'type', 'title', 'description')