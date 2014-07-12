# -*- coding: utf-8 -*-
from django.contrib.admin import site

from bviewer.profile.admin import profile
from bviewer.core.models import Album
from bviewer.profile.admin import ProfileModelAdmin
from bviewer.slideshow.models import SlideShow


class SlideShowAdmin(ProfileModelAdmin):
    list_select_related = True

    fields = ('id', 'album', 'user', 'timer', 'status', 'image_count', 'time',)

    list_display = ('id', 'album_title', 'user', 'timer', 'status', 'image_count', 'time', )
    list_filter = ('album__title', 'time',)
    ordering = ('-time', )

    search_fields = ('album__title', 'user', 'status',)

    def album_title(self, obj):
        return obj.album.title


site.register(SlideShow, SlideShowAdmin)


class SlideShowProfile(SlideShowAdmin):
    fields = ('id', 'album', 'timer', 'status', 'image_count', 'time',)

    list_display = ('id', 'album_title', 'timer', 'status', 'image_count', 'time', )
    list_filter = ('album__title', 'time',)
    ordering = ('-time', )

    readonly_fields = ('id', 'image_count',)

    def has_add_permission(self, request):
        return False

    def queryset(self, request):
        return super(SlideShowProfile, self).queryset(request).filter(album__user=request.user)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        """
        Show in drop down menu only user albums
        """
        if db_field.name == 'album':
            kwargs['queryset'] = Album.objects.filter(user=request.user)
        return super(SlideShowProfile, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.session_key = request.session.session_key
        super(SlideShowProfile, self).save_model(request, obj, form, change)


profile.register(SlideShow, SlideShowProfile)


