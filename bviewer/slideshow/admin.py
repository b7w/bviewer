# -*- coding: utf-8 -*-
from django.contrib.admin import site

from bviewer.profile.admin import profile
from bviewer.core.models import Gallery
from bviewer.profile.admin import ProfileModelAdmin
from bviewer.slideshow.models import SlideShow


class SlideShowAdmin(ProfileModelAdmin):
    list_select_related = True

    fields = ('id', 'gallery', 'user', 'timer', 'status', 'image_count', 'time',)

    list_display = ('id', 'gallery_title', 'user', 'timer', 'status', 'image_count', 'time', )
    list_filter = ('gallery__title', 'time',)
    ordering = ('-time', )

    search_fields = ('gallery__title', 'user', 'status',)

    def gallery_title(self, obj):
        return obj.gallery.title


site.register(SlideShow, SlideShowAdmin)


class SlideShowProfile(SlideShowAdmin):
    fields = ('id', 'gallery', 'timer', 'status', 'image_count', 'time',)

    list_display = ('id', 'gallery_title', 'timer', 'status', 'image_count', 'time', )
    list_filter = ('gallery__title', 'time',)
    ordering = ('-time', )

    readonly_fields = ('id', 'image_count',)

    def has_add_permission(self, request):
        return False

    def queryset(self, request):
        return super(SlideShowProfile, self).queryset(request).filter(gallery__user=request.user)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        """
        Show in drop down menu only user galleries
        """
        if db_field.name == 'gallery':
            kwargs['queryset'] = Gallery.objects.filter(user=request.user)
        return super(SlideShowProfile, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.session_key = request.session.session_key
        super(SlideShowProfile, self).save_model(request, obj, form, change)


profile.register(SlideShow, SlideShowProfile)


