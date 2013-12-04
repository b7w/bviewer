# -*- coding: utf-8 -*-
from django.contrib.admin import site

from bviewer.profile.admin import profile
from bviewer.core.models import Gallery
from bviewer.profile.admin import ProfileModelAdmin
from bviewer.slideshow.models import SlideShow


class SlideShowAdmin(ProfileModelAdmin):
    list_select_related = True

    list_display = ('id', 'gallery_title', 'user', 'session_key', 'status', 'image_count', 'time', )
    list_filter = ('gallery__title', 'time',)
    ordering = ('-time', )

    search_fields = ('gallery__title', 'user', 'status',)

    def gallery_title(self, obj):
        return obj.gallery.title


site.register(SlideShow, SlideShowAdmin)


class SlideShowProfile(SlideShowAdmin):
    list_display = ('gallery_title', 'user', 'session_key', 'status', 'image_count', 'time', )

    def queryset(self, request):
        return super(SlideShowProfile, self).queryset(request).filter(gallery__user=request.user)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        """
        Show in drop down menu only user galleries
        """
        if db_field.name == 'gallery':
            kwargs['queryset'] = Gallery.objects.filter(user=request.user)
        return super(SlideShowProfile, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super(SlideShowProfile, self).get_form(request, obj, **kwargs)
        form.base_fields['session_key'].initial = request.session.session_key
        return form


profile.register(SlideShow, SlideShowProfile)


