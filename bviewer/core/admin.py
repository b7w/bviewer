# -*- coding: utf-8 -*-
import os

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.forms import models

from bviewer.core.utils import RaisingRange
from bviewer.core.models import ProxyUser, Gallery, Image, Video


class ModelAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        """
        Hack to save obj instance to self.user
        """
        self.object = obj
        return super(ModelAdmin, self).get_form(request, obj, **kwargs)


class GalleryAdmin(ModelAdmin):
    list_select_related = True

    list_display = ('title', 'parent', 'user', 'visibility', 'time',)
    list_filter = ('parent__title', 'user__username', 'time', )
    ordering = ('user', 'parent', '-time',)

    search_fields = ('title', 'description',)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'parent' and self.object:
            kwargs['queryset'] = Gallery.objects.filter(user__id=self.object.user.id)
        return super(GalleryAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Gallery, GalleryAdmin)


class ImageAdmin(ModelAdmin):
    list_select_related = True

    list_display = ('path', 'file_name', 'gallery_user', 'gallery_title', 'time', )
    list_filter = ('gallery__title', 'gallery__user__username', 'time',)
    ordering = ('gallery__user__username', 'path', '-time',)

    search_fields = ('gallery__title', 'path',)

    def file_name(self, obj):
        return os.path.basename(obj.path)

    def gallery_title(self, obj):
        return obj.gallery.title

    def gallery_user(self, obj):
        return obj.gallery.user.username

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'gallery' and self.object:
            kwargs['queryset'] = Gallery.objects.filter(user__id=self.object.gallery.user.id)
        return super(ImageAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Image, ImageAdmin)


class VideoAdmin(ModelAdmin):
    list_select_related = True

    list_display = ('gallery_title', 'gallery_user', 'title', 'type', 'uid', 'time', )
    list_filter = ('gallery__title', 'gallery__user__username', 'time',)
    ordering = ('gallery__user__username', '-time',)

    search_fields = ('gallery__title', 'title',)

    def gallery_title(self, obj):
        return obj.gallery.title

    def gallery_user(self, obj):
        return obj.gallery.user.username

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        """
        Show in drop down menu only user galleries and images
        """
        if db_field.name == 'gallery' and self.object:
            kwargs['queryset'] = Gallery.objects.filter(user__id=self.object.gallery.user.id)
        return super(VideoAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Video, VideoAdmin)


class ProxyUserForm(models.ModelForm):
    """
    Set for UserAdmin ProxyUser model except User.
    Add choice field for cache size filed.
    """

    def __init__(self, *args, **kwargs):
        super(ProxyUserForm, self).__init__(*args, **kwargs)
        self._set_choice('cache_size',
            cache_max=ProxyUser.CACHE_SIZE_MAX,
            cache_min=ProxyUser.CACHE_SIZE_MIN,
            base=16
        )
        self._set_choice('cache_archive_size',
            cache_max=ProxyUser.CACHE_ARCHIVE_SIZE_MAX,
            cache_min=ProxyUser.CACHE_ARCHIVE_SIZE_MIN,
            base=64
        )

    def _set_choice(self, field_name, cache_max, cache_min, base):
        raising = RaisingRange(cache_max, start=cache_min, base=base)
        choice = [(i, '%s MB' % i) for i in raising]
        self.fields[field_name] = forms.ChoiceField(choices=choice)

    class Meta(object):
        model = ProxyUser


class ProxyUserAdmin(UserAdmin, ModelAdmin):
    list_select_related = True

    list_display = ('username', 'email', 'is_staff', 'home', 'top_gallery', )

    extra_fieldsets = (
        ('Viewer info', {'fields': ('url', 'top_gallery', 'cache_size', 'cache_archive_size', )}),
        ('Additional info', {'fields': ('about_title', 'about_text',)}),
    )
    fieldsets = UserAdmin.fieldsets[:2] + extra_fieldsets + UserAdmin.fieldsets[2:]

    readonly_fields = ('password', 'is_active', 'is_staff', 'last_login', 'date_joined', )
    form = ProxyUserForm

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        """
        Show in drop down menu only user galleries and images
        """
        if db_field.name == 'top_gallery' and self.object:
            kwargs['queryset'] = Gallery.objects.filter(user__id=self.object.id)
        return super(UserAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(ProxyUser, ProxyUserAdmin)