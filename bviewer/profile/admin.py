# -*- coding: utf-8 -*-

from django.contrib.admin import StackedInline, site
from django.contrib.auth.admin import UserAdmin

from bviewer.core.admin import ModelAdmin, ProxyUserForm
from bviewer.core.models import Gallery, Image
from bviewer.profile.models import ProfileProxyUser, ProfileGallery, ProfileImage, ProfileVideo


class ImageInline(StackedInline):
    model = ProfileImage
    fk_name = 'gallery'


class ProfileGalleryAdmin(ModelAdmin):
    list_select_related = True

    list_display = ('title', 'parent', 'private', 'time',)
    list_filter = ('parent__title', 'time', )
    ordering = ('parent', 'time',)

    fields = ('parent', 'title', 'private', 'description', 'thumbnail', 'time')

    inlines = [ImageInline, ]

    def queryset(self, request):
        return super(ProfileGalleryAdmin, self).queryset(request).filter(user=request.user)

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'parent' and self.object:
            kwargs['queryset'] = Gallery.objects.filter(user__id=self.object.user.id)
        return super(ProfileGalleryAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


site.register(ProfileGallery, ProfileGalleryAdmin)


class ProfileImageAdmin(ModelAdmin):
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


site.register(ProfileImage, ProfileImageAdmin)


class ProfileVideoAdmin(ModelAdmin):
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


site.register(ProfileVideo, ProfileVideoAdmin)


class ProfileUserAdmin(UserAdmin, ModelAdmin):
    list_select_related = True
    list_display = ('username', 'email', 'home', 'top_gallery', 'is_staff', )
    list_filter = ()
    fieldsets = (
        ('Personal info', {'fields': ('url', 'home', 'cache_size', 'top_gallery', 'about_title', 'about_text', 'avatar',)}),
        ('Important dates', {'fields': ('last_login', 'date_joined',)}),
    )
    readonly_fields = ('password', 'last_login', 'date_joined', )
    form = ProxyUserForm

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
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


site.register(ProfileProxyUser, ProfileUserAdmin)