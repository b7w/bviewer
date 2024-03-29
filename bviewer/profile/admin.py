# -*- coding: utf-8 -*-
import os
from collections import Counter

from django.contrib.admin import AdminSite, ModelAdmin, TabularInline
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils.encoding import smart_text

from bviewer.core.controllers import AlbumController
from bviewer.core.files.storage import ImageStorage
from bviewer.core.models import Access, Album, Image, Gallery, Video
from bviewer.profile.actions import bulk_time_update, update_time_from_exif
from bviewer.profile.forms import AdminGalleryForm, AdminAlbumForm


class ProfileSite(AdminSite):
    """
    Separate admin site only to edit user albums, images, profile
    """
    site_title = 'Profile'
    site_header = 'User profile'
    index_title = 'Home'

    def __init__(self, name='profile'):
        super(ProfileSite, self).__init__(name)

    def has_permission(self, request):
        user = request.user
        return user.is_active and user.has_perm('core.user_holder')


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


class ProfileUserAdmin(UserAdmin):
    list_select_related = True

    list_display = ('username', 'email')

    readonly_fields = ('username', 'is_active', 'last_login', 'date_joined', 'user_permissions', )
    fieldsets = (
        ('Account info', {'fields': ('username', 'password', 'is_active',)}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email',)}),
        ('Important dates', {'fields': ('last_login', 'date_joined',)}),
    )

    def get_queryset(self, request):
        return super(ProfileUserAdmin, self).get_queryset(request).filter(id=request.user.id)


profile.register(User, ProfileUserAdmin)


class ProfileAccessAdmin(ProfileModelAdmin):
    list_select_related = True

    list_display = ('user', 'gallery', 'is_active', )
    list_filter = ('user', 'gallery', 'is_active', )

    ordering = ('gallery',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if change and 'is_active' in form.changed_data:
            if obj.is_active and not obj.user.is_active:
                obj.user.is_active = True
                obj.user.save()
        super(ProfileAccessAdmin, self).save_model(request, obj, form, change)


profile.register(Access, ProfileAccessAdmin)


class AccessInline(TabularInline):
    model = Access
    verbose_name = 'Visible to user'
    verbose_name_plural = 'Visible to users'
    can_delete = False
    extra = 0


class ProfileGalleryAdmin(ProfileModelAdmin):
    list_select_related = True
    form = AdminGalleryForm

    inlines = (AccessInline,)

    list_display = ('url', 'top_album', 'description', )
    exclude = ('user',)

    readonly_fields = ('home', 'cache_info', )

    ordering = ('url',)

    def cache_info(self, user):
        storage = ImageStorage(user)
        images_size = storage.cache_size() / 2 ** 20
        storage = ImageStorage(user, archive_cache=True)
        archive_size = storage.cache_size() / 2 ** 20
        return 'Images size: {0:.1f} MB, archives size: {1:.1f} MB'.format(images_size, archive_size)

    def has_add_permission(self, request):
        return False

    def get_queryset(self, request):
        return super(ProfileGalleryAdmin, self).get_queryset(request).filter(user=request.user)

    def get_form(self, request, obj=None, **kwargs):
        # Add default user
        data = request.POST.copy()
        data['user'] = request.user.id
        request.POST = data
        return super(ProfileGalleryAdmin, self).get_form(request, obj=None, **kwargs)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        """
        Show in drop down menu only user albums
        """
        if db_field.name == 'top_album':
            kwargs['queryset'] = Album.objects.filter(gallery__user=request.user)
        return super(ProfileGalleryAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


profile.register(Gallery, ProfileGalleryAdmin)


class ProfileAlbumAdmin(ProfileModelAdmin):
    list_select_related = True
    form = AdminAlbumForm

    readonly_fields = ('images', 'pre_cache', 'thumbnails',)
    fields = ('gallery', 'parent', 'title', 'visibility', 'album_sorting', 'allow_archiving',
              'images', 'pre_cache', 'description', 'time', 'thumbnails', )
    list_display = ('title', 'parent', 'gallery', 'visibility', 'images', 'time',)

    list_filter = ('gallery', 'parent__title', 'time', )
    search_fields = ('title', 'description',)

    ordering = ('parent', '-time',)

    def images(self, obj):
        if Album.objects.safe_get(id=obj.id):
            params = dict(gallery_id=obj.gallery_id, album_id=obj.id)
            url = reverse('profile.album', kwargs=params)
            path = self.images_expected_path(obj)
            count = Image.objects.filter(album=obj).count()
            return smart_text('<b><a href="{url}?p={p}">Select images on disk ({count})</a></b>') \
                .format(url=url, p=path, count=count)
        return smart_text('<b>Save album first to select images</b>')

    images.allow_tags = True

    def pre_cache(self, obj):
        if Album.objects.safe_get(id=obj.id):
            params = dict(gallery_id=obj.gallery_id, album_id=obj.id)
            url = reverse('profile.album.pre-cache', kwargs=params)
            return smart_text('<b><a href="{url}">Run pre cache task</a></b>').format(url=url)
        return smart_text('<b>Save album first</b>')

    pre_cache.allow_tags = True

    def images_expected_path(self, album):
        """
        Get some album images
        and detect most popular directory where they stored.
        If will save some clicks in UI.
        """
        images = Image.objects.filter(album=album)[:8]
        dir_paths = [os.path.dirname(i.path) for i in images]
        most_common = Counter(dir_paths).most_common(1)
        if most_common:
            path, count = most_common[0]
            return path
        return ''

    def thumbnails(self, obj):
        context = dict(images=Image.objects.filter(album=obj.id), obj=obj)
        return render_to_string('profile/thumbnails.html', context).replace('\r\n', '')

    thumbnails.allow_tags = True
    thumbnails.short_description = 'Album thumbnail'

    def get_queryset(self, request):
        return super(ProfileAlbumAdmin, self).get_queryset(request).filter(gallery__user=request.user)

    def save_model(self, request, obj, form, change):
        thumbnail_id = form.data['thumbnail_id']
        if thumbnail_id != 'None':
            obj.thumbnail_id = thumbnail_id
        else:
            obj.thumbnail = None
        controller = AlbumController.from_obj(obj)
        # allow archiving
        if change and 'allow_archiving' in form.changed_data:
            controller.set_archiving(obj.allow_archiving)
        if change and 'gallery' in form.changed_data:
            controller.set_gallery(obj.gallery)
        super(ProfileAlbumAdmin, self).save_model(request, obj, form, change)

    class Media(object):
        css = {
            'all': ('profile/css/profile.css',)
        }


profile.register(Album, ProfileAlbumAdmin)


class ProfileImageAdmin(ProfileModelAdmin):
    list_select_related = True
    actions = [bulk_time_update, update_time_from_exif, ]

    readonly_fields = ('image_thumbnail',)
    list_display = ('path', 'file_name', 'album_title', 'image_thumbnail_popup', 'time', )

    list_filter = ('album__title', 'time',)
    search_fields = ('album__title', 'path',)

    ordering = ('-time', 'album', )

    def file_name(self, obj):
        return os.path.basename(obj.path)

    def album_title(self, obj):
        return obj.album.title

    def image_thumbnail(self, obj):
        params = dict(gallery_id=obj.album.gallery_id)
        url = reverse('profile.download', kwargs=params)
        return smart_text('<img class="thumbnail" src="{0}?p={1}">').format(url, obj.path)

    image_thumbnail.allow_tags = True

    def image_thumbnail_popup(self, obj):
        params = dict(gallery_id=obj.album.gallery_id)
        url = reverse('profile.download', kwargs=params)
        return smart_text('<img class="preview" src="{0}?p={1}">').format(url, obj.path)

    image_thumbnail_popup.allow_tags = True

    def get_queryset(self, request):
        return super(ProfileImageAdmin, self).get_queryset(request).filter(album__gallery__user=request.user)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        """
        Show in drop down menu only user albums
        """
        if db_field.name == 'album':
            kwargs['queryset'] = Album.objects.filter(gallery__user=request.user)
        return super(ProfileImageAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        css = {
            'all': ('profile/css/profile.css',)
        }


profile.register(Image, ProfileImageAdmin)


class ProfileVideoAdmin(ProfileModelAdmin):
    list_select_related = True

    list_display = ('album_title', 'title', 'type', 'uid', 'time', )

    list_filter = ('album__title', 'type', 'time',)
    search_fields = ('album__title', 'title',)

    ordering = ('-time', 'album', )

    def album_title(self, obj):
        return obj.album.title

    def get_queryset(self, request):
        return super(ProfileVideoAdmin, self).get_queryset(request).filter(album__gallery__user=request.user)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        """
        Show in drop down menu only user albums
        """
        if db_field.name == 'album':
            kwargs['queryset'] = Album.objects.filter(gallery__user=request.user)
        return super(ProfileVideoAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


profile.register(Video, ProfileVideoAdmin)