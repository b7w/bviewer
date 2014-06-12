# -*- coding: utf-8 -*-
import os

from django.contrib.admin import site, ModelAdmin
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.contrib.auth.forms import UserChangeForm

from bviewer.core.utils import RaisingRange
from bviewer.core.models import Gallery, Album, Image, Video


class AlbumAdmin(ModelAdmin):
    list_select_related = True

    list_display = ('title', 'parent', 'user', 'visibility', 'time',)
    list_filter = ('parent__title', 'user__username', 'time', )
    ordering = ('user', 'parent', '-time',)

    search_fields = ('title', 'description',)


site.register(Album, AlbumAdmin)


class ImageAdmin(ModelAdmin):
    list_select_related = True

    list_display = ('path', 'file_name', 'album_user', 'album_title', 'time', )
    list_filter = ('album__title', 'album__user__username', 'time',)
    ordering = ('album__user__username', 'path', '-time',)

    search_fields = ('album__title', 'path',)

    def file_name(self, obj):
        return os.path.basename(obj.path)

    def album_title(self, obj):
        return obj.album.title

    def album_user(self, obj):
        return obj.album.user.username


site.register(Image, ImageAdmin)


class VideoAdmin(ModelAdmin):
    list_select_related = True

    list_display = ('album_title', 'album_user', 'title', 'type', 'uid', 'time', )
    list_filter = ('album__title', 'album__user__username', 'time',)
    ordering = ('album__user__username', '-time',)

    search_fields = ('album__title', 'title',)

    def album_title(self, obj):
        return obj.album.title

    def album_user(self, obj):
        return obj.album.user.username


site.register(Video, VideoAdmin)


class GalleryForm(UserChangeForm):
    """
    Set for UserAdmin Gallery model except User.
    Add choice field for cache size filed.
    """

    def __init__(self, *args, **kwargs):
        super(GalleryForm, self).__init__(*args, **kwargs)
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
        self.fields[field_name] = forms.ChoiceField(choices=choice)

    class Meta(object):
        model = Gallery


class GalleryAdmin(UserAdmin, ModelAdmin):
    list_select_related = True

    list_display = ('username', 'email', 'is_staff', 'home', 'top_album', )

    extra_fieldsets = (
        ('Account info', {'fields': ('username', 'password', )}),
        ('Personal info', {'fields': ('email', 'first_name', 'last_name', )}),
        ('Viewer info', {'fields': ('url', 'home', 'top_album', 'cache_size', 'cache_archive_size', )}),
        ('Additional info', {'fields': ('about_title', 'about_text',)}),
    )
    fieldsets = extra_fieldsets + UserAdmin.fieldsets[2:]
    readonly_fields = ('is_active', 'is_staff', 'last_login', 'date_joined', )

    form = GalleryForm


site.register(Gallery, GalleryAdmin)