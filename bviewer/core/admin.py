# -*- coding: utf-8 -*-


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
    list_display = ("title", "parent", "user", "private", "time",)
    list_filter = (  "parent__title", "user__username", "time", )
    ordering = ("user", "parent", "time",)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        print self.object
        if db_field.name == "parent" and self.object:
            kwargs["queryset"] = Gallery.objects.filter(user__id=self.object.user.id)
        return super(GalleryAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(Gallery, GalleryAdmin)


class ImageAdmin(ModelAdmin):
    list_select_related = True
    list_display = ("gallery_title", "gallery_user", "path", )
    list_filter = ( "gallery__title", "gallery__user__username", )
    ordering = ("gallery__user__username", "path",)

    def gallery_title(self, obj):
        return obj.gallery.title

    def gallery_user(self, obj):
        return obj.gallery.user.username

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "gallery" and self.object:
            kwargs["queryset"] = Gallery.objects.filter(user__id=self.object.gallery.user.id)
        return super(ImageAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(Image, ImageAdmin)


class VideoAdmin(ModelAdmin):
    list_select_related = True
    list_display = ("gallery_title", "gallery_user", "title", "uid",)
    list_filter = ( "gallery__title", "gallery__user__username", )
    ordering = ("gallery__user__username", "uid",)

    def gallery_title(self, obj):
        return obj.gallery.title

    def gallery_user(self, obj):
        return obj.gallery.user.username

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Show in drop down menu only user galleries and images
        """
        if db_field.name == "gallery" and self.object:
            kwargs["queryset"] = Gallery.objects.filter(user__id=self.object.gallery.user.id)
        return super(VideoAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(Video, VideoAdmin)


class ProxyUserForm(models.ModelForm):
    """
    Set for UserAdmin ProxyUser model except User.
    Add choice field for cache size filed.
    """

    def __init__(self, *args, **kwargs):
        self.range = RaisingRange(512, start=16, base=16)
        self.choice = [(i, "%s MB" % i) for i in self.range]
        super(ProxyUserForm, self).__init__(*args, **kwargs)
        self.fields['cache_size'] = forms.ChoiceField(choices=self.choice)

    class Meta:
        model = ProxyUser


class UserAdmin(UserAdmin, ModelAdmin):
    list_select_related = True
    list_display = ("username", "email", "is_staff", "home", "top_gallery", )
    fieldsets = (
        ("Main", {"fields": ("username", "email", "password",)}),
        ("Personal info", {"fields": ("url", "home", "cache_size", "top_gallery", "about_title", "about_text", "avatar",)}),
        ("Permissions", {"fields": ("is_active", "is_staff",)}),
        ("Important dates", {"fields": ("last_login", "date_joined",)}),
        )
    readonly_fields = ( "password", "is_active", "is_staff", "last_login", "date_joined", )
    form = ProxyUserForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Show in drop down menu only user galleries and images
        """
        if db_field.name == "top_gallery" and self.object:
            kwargs["queryset"] = Gallery.objects.filter(user__id=self.object.id)
        if db_field.name == "avatar" and self.object:
            kwargs["queryset"] = Image.objects.filter(gallery__user__id=self.object.id)
        return super(UserAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(ProxyUser, UserAdmin)