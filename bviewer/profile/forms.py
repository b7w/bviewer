# -*- coding: utf-8 -*-
import re
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.forms import Form, ModelForm, ChoiceField, CharField, MultipleHiddenInput

from bviewer.core.models import Gallery, Album, Video
from bviewer.core.utils import RaisingRange


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
        self._set_choice('cache_size',
                         cache_max=Gallery.CACHE_SIZE_MAX,
                         cache_min=Gallery.CACHE_SIZE_MIN,
                         base=16
        )
        self._set_choice('cache_archive_size',
                         cache_max=Gallery.CACHE_ARCHIVE_SIZE_MAX,
                         cache_min=Gallery.CACHE_ARCHIVE_SIZE_MIN,
                         base=64
        )

    def _set_choice(self, field_name, cache_max, cache_min, base):
        raising = RaisingRange(cache_max, start=cache_min, base=base)
        choice = [(i, '%s MB' % i) for i in raising]
        self.fields[field_name] = ChoiceField(choices=choice)

    class Meta(object):
        model = Gallery


class AdminAlbumForm(ModelForm):
    def clean_title(self):
        title = self.cleaned_data['title']
        user_id = self.data['user']
        if Album.objects.filter(title=title, user_id=user_id).exclude(id=self.instance.id).count() > 0:
            raise ValidationError('Title must be unique')
        return title

    class Meta(object):
        model = Album


class AlbumForm(ModelForm):
    class Meta(object):
        model = Album
        fields = ('title', 'visibility', 'description', 'time')


class VideoForm(ModelForm):
    class Meta(object):
        model = Video
        fields = ('uid', 'type', 'title', 'description')