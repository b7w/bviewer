# -*- coding: utf-8 -*-

from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

from bviewer.core.admin import ModelAdmin, ProxyUserForm
from bviewer.core.models import Gallery, Image, ProxyUser
from bviewer.profile.models import ProfileProxyUser, ProfileGallery, ProfileVideo, ProfileImage


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

    list_display = ('title', 'parent', 'private', 'images', 'time',)
    list_filter = ('parent__title', 'time', )
    ordering = ('parent', 'time',)

    readonly_fields = ('images', 'thumbnails',)
    fields = ('parent', 'title', 'private', 'images', 'description', 'time', 'thumbnails', )

    def images(self, obj):
        return '<b><a href="{0}#!g={1}">edit</a></b>'.format(reverse('profile.images'), obj.id)

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
        print(1, thumbnail_id)
        if thumbnail_id != 'None':
            obj.thumbnail_id = thumbnail_id
        else:
            obj.thumbnail = None
        obj.save()

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'parent' and self.object:
            kwargs['queryset'] = Gallery.objects.filter(user__id=self.object.user.id)
        return super(ProfileGalleryAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        css = {
            'all': ('profile/css/profile.css',)
        }


profile.register(ProfileGallery, ProfileGalleryAdmin)


class ProfileImageAdmin(ProfileModelAdmin):
    list_select_related = True

    list_display = ('gallery_title', 'path', )
    list_filter = ('gallery__title', )
    ordering = ('gallery__user__username', 'path',)

    def gallery_title(self, obj):
        return obj.gallery.title

    def gallery_user(self, obj):
        return obj.gallery.user.username

    def queryset(self, request):
        return super(ProfileImageAdmin, self).queryset(request).filter(gallery__user=request.user)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'gallery' and self.object:
            kwargs['queryset'] = Gallery.objects.filter(user__id=self.object.gallery.user.id)
        return super(ProfileImageAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


profile.register(ProfileImage, ProfileImageAdmin)


class ProfileVideoAdmin(ProfileModelAdmin):
    list_select_related = True

    list_display = ('gallery_title', 'title', 'type', 'uid',)
    list_filter = ('gallery__title', 'type', )
    ordering = ('gallery__title',)

    def gallery_title(self, obj):
        return obj.gallery.title

    def gallery_user(self, obj):
        return obj.gallery.user.username

    def queryset(self, request):
        return super(ProfileVideoAdmin, self).queryset(request).filter(gallery__user=request.user)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        """
        Show in drop down menu only user galleries and images
        """
        if db_field.name == 'gallery' and self.object:
            kwargs['queryset'] = Gallery.objects.filter(user__id=self.object.gallery.user.id)
        return super(ProfileVideoAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


profile.register(ProfileVideo, ProfileVideoAdmin)


class ProfileUserAdmin(UserAdmin, ProfileModelAdmin):
    list_select_related = True
    list_display = ('username', 'email', 'top_gallery', 'is_staff', )
    list_filter = ()
    fieldsets = (
        ('Personal info', {'fields': ('url', 'cache_size', 'top_gallery', 'about_title', 'about_text', 'avatar',)}),
        ('Important dates', {'fields': ('last_login', 'date_joined',)}),
    )
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
        if db_field.name == 'avatar' and self.object:
            kwargs['queryset'] = Image.objects.filter(gallery__user__id=self.object.id)
        return super(ProfileUserAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


profile.register(ProfileProxyUser, ProfileUserAdmin)