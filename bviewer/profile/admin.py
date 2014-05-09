# -*- coding: utf-8 -*-
from collections import Counter
import os

from django.contrib.admin import AdminSite, ModelAdmin
from django.contrib.auth.admin import UserAdmin
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils.encoding import smart_text

from bviewer.core.admin import ProxyUserForm
from bviewer.core.files.storage import ImageStorage
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
        if Gallery.objects.safe_get(id=obj.id):
            url = reverse('profile.gallery', kwargs=dict(uid=obj.id))
            path = self.images_expected_path(obj)
            count = Image.objects.filter(gallery=obj).count()
            return smart_text('<b><a href="{url}?p={p}">Select images on disk ({count})</a></b>') \
                .format(url=url, p=path, count=count)
        return smart_text('<b>Save gallery first to select images</b>')

    images.allow_tags = True

    def images_expected_path(self, gallery):
        """
        Get some gallery images
        and detect most popular directory where they stored.
        If will save some clicks in UI.
        """
        images = Image.objects.filter(gallery=gallery)[:8]
        dir_paths = [os.path.dirname(i.path) for i in images]
        most_common = Counter(dir_paths).most_common(1)
        if most_common:
            path, count = most_common[0]
            return path
        return ''

    def thumbnails(self, obj):
        context = dict(images=Image.objects.filter(gallery=obj.id), obj=obj)
        return render_to_string('profile/thumbnails.html', context).replace('\r\n', '')

    thumbnails.allow_tags = True
    thumbnails.short_description = 'Gallery thumbnail'

    def queryset(self, request):
        return super(ProfileGalleryAdmin, self).queryset(request).filter(user=request.user)

    def save_model(self, request, obj, form, change):
        obj.user = ProxyUser.objects.get(pk=request.user.pk)
        if not obj.parent:
            obj.parent = obj.user.top_gallery
        thumbnail_id = form.data['thumbnail_id']
        if thumbnail_id != 'None':
            obj.thumbnail_id = thumbnail_id
        else:
            obj.thumbnail = None
        obj.save()

    def add_view(self, request, form_url='', extra_context=None):
        # Add default parent Welcome gallery
        data = request.GET.copy()
        data['parent'] = ProxyUser.objects.get(pk=request.user.pk).top_gallery_id
        request.GET = data
        return super(ProfileGalleryAdmin, self).add_view(request, form_url, extra_context)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        """
        Show in drop down menu only user galleries
        """
        if db_field.name == 'parent':
            kwargs['queryset'] = Gallery.objects.filter(user=request.user)
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
        """
        Show in drop down menu only user galleries
        """
        if db_field.name == 'gallery':
            kwargs['queryset'] = Gallery.objects.filter(user=request.user)
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
        Show in drop down menu only user galleries
        """
        if db_field.name == 'gallery':
            kwargs['queryset'] = Gallery.objects.filter(user=request.user)
        return super(ProfileVideoAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


profile.register(Video, ProfileVideoAdmin)


class ProfileUserAdmin(ProfileModelAdmin, UserAdmin):
    list_select_related = True

    list_display = ('username', 'url', 'email', 'top_gallery', 'is_staff', )
    list_filter = ()

    fieldsets = (
        ('Account info', {'fields': ('username', 'password', )}),
        ('Personal info', {'fields': ('email', 'first_name', 'last_name', )}),
        ('Viewer info', {'fields': ('url', 'top_gallery', 'cache_size', 'cache_archive_size', 'cache_info', )}),
        ('Additional info', {'fields': ('about_title', 'about_text', )}),
        ('Important dates', {'fields': ('last_login', 'date_joined', )}),
    )
    readonly_fields = ('last_login', 'date_joined', 'cache_info', )

    form = ProxyUserForm

    def cache_info(self, user):
        storage = ImageStorage(user)
        images_size = storage.cache_size() / 2 ** 20
        storage = ImageStorage(user, archive_cache=True)
        archive_size = storage.cache_size() / 2 ** 20
        return 'Images size: {0} MB, archives size: {1} MB'.format(images_size, archive_size)

    def has_add_permission(self, request):
        return False

    def queryset(self, request):
        return super(ProfileUserAdmin, self).queryset(request).filter(id=request.user.id)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        """
        Show in drop down menu only user galleries
        """
        if db_field.name == 'top_gallery':
            kwargs['queryset'] = Gallery.objects.filter(user=request.user)
        return super(ProfileUserAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


profile.register(ProxyUser, ProfileUserAdmin)