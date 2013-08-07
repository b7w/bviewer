# -*- coding: utf-8 -*-
import os

from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

from bviewer.core.admin import ModelAdmin, ProxyUserForm
from bviewer.core.models import Gallery, Image, ProxyUser, Video


class ProfileSite(AdminSite):
    """
    Separate admin site only to edit user galleries, images, profile
    """

    def __init__(self, name='profile', app_name='admin'):
        super(ProfileSite, self).__init__(name, app_name)

    def has_permission(self, request):
        user = request.user
        return user.is_active and request.user.has_perm('core.user_holder')


profile = ProfileSite()


class ProfileModelAdmin(ModelAdmin):
    """
    Override permissions, get from `ProfileSite.has_permission`
    """

    def has_add_permission(self, request):
        return self.admin_site.has_permission(request)

    def has_change_permission(self, request, obj=None):
        return self.admin_site.has_permission(request)

    def has_delete_permission(self, request, obj=None):
        return self.admin_site.has_permission(request)


class ProfileGalleryAdmin(ProfileModelAdmin):
    list_select_related = True

    list_display = ('title', 'parent', 'visibility', 'images', 'time',)
    list_filter = ('parent__title', 'time', )
    ordering = ('parent', '-time',)

    search_fields = ('title', 'description',)

    readonly_fields = ('images', 'thumbnails',)
    fields = ('parent', 'title', 'visibility', 'gallery_sorting', 'images', 'description', 'time', 'thumbnails', )

    def images(self, obj):
        gl_count = Image.objects.filter(gallery=obj).count()
        return '<b><a href="{0}">Select images on disk ({1})</a></b>' \
            .format(reverse('profile.gallery', kwargs=dict(uid=obj.id)), gl_count)

    images.allow_tags = True

    def thumbnails(self, obj):
        context = dict(images=Image.objects.filter(gallery=obj.id), obj=obj)
        return render_to_string('profile/thumbnails.html', context).replace('\r\n', '')

    thumbnails.allow_tags = True
    thumbnails.short_description = 'Gallery thumbnail'

    def queryset(self, request):
        return super(ProfileGalleryAdmin, self).queryset(request).filter(user=request.user)

    def save_model(self, request, obj, form, change):
        obj.user = ProxyUser.objects.get(pk=request.user.pk)
        thumbnail_id = form.data['thumbnail_id']
        if thumbnail_id != 'None':
            obj.thumbnail_id = thumbnail_id
        else:
            obj.thumbnail = None
        obj.save()

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'parent' and self.object:
            kwargs['queryset'] = Gallery.objects.filter(user__id=self.object.user.id)
        return super(ProfileGalleryAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    class Media(object):
        css = {
            'all': ('profile/css/profile.css',)
        }


profile.register(Gallery, ProfileGalleryAdmin)


class ProfileImageAdmin(ProfileModelAdmin):
    list_select_related = True

    list_display = ('path', 'file_name', 'gallery_title', 'time', )
    list_filter = ('gallery__title', 'time',)
    ordering = ('-time', 'gallery', )

    search_fields = ('gallery__title', 'path',)

    def file_name(self, obj):
        return os.path.basename(obj.path)

    def gallery_title(self, obj):
        return obj.gallery.title

    def queryset(self, request):
        return super(ProfileImageAdmin, self).queryset(request).filter(gallery__user=request.user)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'gallery' and self.object:
            kwargs['queryset'] = Gallery.objects.filter(user__id=self.object.gallery.user.id)
        return super(ProfileImageAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


profile.register(Image, ProfileImageAdmin)


class ProfileVideoAdmin(ProfileModelAdmin):
    list_select_related = True

    list_display = ('gallery_title', 'title', 'type', 'uid', 'time', )
    list_filter = ('gallery__title', 'type', 'time',)
    ordering = ('-time', 'gallery', )

    search_fields = ('gallery__title', 'title',)

    def gallery_title(self, obj):
        return obj.gallery.title

    def queryset(self, request):
        return super(ProfileVideoAdmin, self).queryset(request).filter(gallery__user=request.user)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        """
        Show in drop down menu only user galleries and images
        """
        if db_field.name == 'gallery' and self.object:
            kwargs['queryset'] = Gallery.objects.filter(user__id=self.object.gallery.user.id)
        return super(ProfileVideoAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


profile.register(Video, ProfileVideoAdmin)


class ProfileUserAdmin(ProfileModelAdmin, UserAdmin):
    list_select_related = True

    list_display = ('username', 'email', 'top_gallery', 'is_staff', )
    list_filter = ()

    extra_fieldsets = (
        ('Viewer info', {'fields': ('url', 'top_gallery', 'cache_size', 'cache_archive_size', )}),
        ('Additional info', {'fields': ('about_title', 'about_text',)}),
    )
    # Model field + important dates
    fieldsets = extra_fieldsets + UserAdmin.fieldsets[-1:]
    readonly_fields = ('password', 'last_login', 'date_joined', )

    form = ProxyUserForm

    def has_add_permission(self, request):
        return False

    def queryset(self, request):
        return super(ProfileUserAdmin, self).queryset(request).filter(id=request.user.id)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        """
        Show in drop down menu only user galleries and images
        """
        if db_field.name == 'top_gallery' and self.object:
            kwargs['queryset'] = Gallery.objects.filter(user__id=self.object.id)
        return super(ProfileUserAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


profile.register(ProxyUser, ProfileUserAdmin)