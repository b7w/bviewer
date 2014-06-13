# -*- coding: utf-8 -*-
import os

from django.contrib.admin import site, ModelAdmin

from bviewer.core.models import Gallery, Album, Image, Video


class GalleryAdmin(ModelAdmin):
    list_select_related = True


site.register(Gallery, GalleryAdmin)


class AlbumAdmin(ModelAdmin):
    list_select_related = True

    ordering = ('gallery', 'parent', '-time',)

    search_fields = ('title', 'description',)


site.register(Album, AlbumAdmin)


class ImageAdmin(ModelAdmin):
    list_select_related = True

    list_display = ('path', 'file_name', 'album_user', 'album_title', 'time', )
    list_filter = ('album__title', 'album__gallery__user__username', 'time',)
    ordering = ('album__gallery__user__username', 'path', '-time',)

    search_fields = ('album__title', 'path',)

    def file_name(self, obj):
        return os.path.basename(obj.path)

    def album_title(self, obj):
        return obj.album.title

    def album_user(self, obj):
        return obj.album.gallery.user.username


site.register(Image, ImageAdmin)


class VideoAdmin(ModelAdmin):
    list_select_related = True

    list_display = ('album_title', 'album_user', 'title', 'type', 'uid', 'time', )
    list_filter = ('album__title', 'album__gallery__user__username', 'time',)
    ordering = ('album__gallery__user__username', '-time',)

    search_fields = ('album__title', 'title',)

    def album_title(self, obj):
        return obj.album.title

    def album_user(self, obj):
        return obj.album.gallery.user.username


site.register(Video, VideoAdmin)
