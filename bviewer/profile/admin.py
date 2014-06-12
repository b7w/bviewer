# -*- coding: utf-8 -*-
import os
from collections import Counter
from django.contrib.admin import AdminSite, ModelAdmin
from django.contrib.auth.admin import UserAdmin
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils.encoding import smart_text

from bviewer.core.admin import ProxyUserForm
from bviewer.core.controllers import AlbumController
from bviewer.core.files.storage import ImageStorage
from bviewer.core.models import Album, Image, ProxyUser, Video
from bviewer.profile.actions import bulk_time_update, update_time_from_exif
from bviewer.profile.forms import AdminAlbumForm


class ProfileSite(AdminSite):
    """
    Separate admin site only to edit user albums, images, profile
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


class ProfileAlbumAdmin(ProfileModelAdmin):
    list_select_related = True
    form = AdminAlbumForm

    list_display = ('title', 'parent', 'visibility', 'images', 'time',)
    list_filter = ('parent__title', 'time', )
    ordering = ('parent', '-time',)

    search_fields = ('title', 'description',)

    readonly_fields = ('images', 'pre_cache', 'thumbnails',)
    fields = ('parent', 'title', 'visibility', 'album_sorting', 'allow_archiving',
              'images', 'pre_cache', 'description', 'time', 'thumbnails', )

    def images(self, obj):
        if Album.objects.safe_get(id=obj.id):
            url = reverse('profile.album', kwargs=dict(uid=obj.id))
            path = self.images_expected_path(obj)
            count = Image.objects.filter(album=obj).count()
            return smart_text('<b><a href="{url}?p={p}">Select images on disk ({count})</a></b>') \
                .format(url=url, p=path, count=count)
        return smart_text('<b>Save album first to select images</b>')

    images.allow_tags = True

    def pre_cache(self, obj):
        if Album.objects.safe_get(id=obj.id):
            url = reverse('profile.album.pre-cache', kwargs=dict(uid=obj.id))
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

    def queryset(self, request):
        return super(ProfileAlbumAdmin, self).queryset(request).filter(user=request.user)

    def save_model(self, request, obj, form, change):
        obj.user = ProxyUser.objects.get(pk=request.user.pk)
        if not obj.parent:
            obj.parent = obj.user.top_album
        thumbnail_id = form.data['thumbnail_id']
        if thumbnail_id != 'None':
            obj.thumbnail_id = thumbnail_id
        else:
            obj.thumbnail = None
        # allow archiving
        if change and 'allow_archiving' in form.changed_data:
            controller = AlbumController.from_obj(obj)
            controller.set_archiving(obj.allow_archiving)
        super(ProfileAlbumAdmin, self).save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        # Add default parent Welcome album
        user = ProxyUser.objects.get(pk=request.user.pk)
        data = request.GET.copy()
        data['parent'] = user.top_album_id
        request.GET = data
        # Add default user
        data = request.POST.copy()
        data['user'] = user.id
        request.POST = data
        return super(ProfileAlbumAdmin, self).get_form(request, obj=None, **kwargs)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        """
        Show in drop down menu only user albums
        """
        if db_field.name == 'parent':
            kwargs['queryset'] = Album.objects.filter(user=request.user)
        return super(ProfileAlbumAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    class Media(object):
        css = {
            'all': ('profile/css/profile.css',)
        }


profile.register(Album, ProfileAlbumAdmin)


class ProfileImageAdmin(ProfileModelAdmin):
    list_select_related = True
    actions = [bulk_time_update, update_time_from_exif, ]

    list_display = ('path', 'file_name', 'album_title', 'image_thumbnail_popup', 'time', )
    list_filter = ('album__title', 'time',)
    ordering = ('-time', 'album', )

    readonly_fields = ('image_thumbnail',)
    search_fields = ('album__title', 'path',)

    def file_name(self, obj):
        return os.path.basename(obj.path)

    def album_title(self, obj):
        return obj.album.title

    def image_thumbnail(self, obj):
        url = reverse('core.download', kwargs=dict(size='small', uid=obj.id))
        return smart_text('<img class="thumbnail" src="{0}">').format(url)

    image_thumbnail.allow_tags = True

    def image_thumbnail_popup(self, obj):
        url = reverse('core.download', kwargs=dict(size='tiny', uid=obj.id))
        return smart_text('<img class="preview" src="{0}">').format(url)

    image_thumbnail_popup.allow_tags = True

    def queryset(self, request):
        return super(ProfileImageAdmin, self).queryset(request).filter(album__user=request.user)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        """
        Show in drop down menu only user albums
        """
        if db_field.name == 'album':
            kwargs['queryset'] = Album.objects.filter(user=request.user)
        return super(ProfileImageAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        css = {
            'all': ('profile/css/profile.css',)
        }
        js = ('my_code.js',)


profile.register(Image, ProfileImageAdmin)


class ProfileVideoAdmin(ProfileModelAdmin):
    list_select_related = True

    list_display = ('album_title', 'title', 'type', 'uid', 'time', )
    list_filter = ('album__title', 'type', 'time',)
    ordering = ('-time', 'album', )

    search_fields = ('album__title', 'title',)

    def album_title(self, obj):
        return obj.album.title

    def queryset(self, request):
        return super(ProfileVideoAdmin, self).queryset(request).filter(album__user=request.user)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        """
        Show in drop down menu only user albums
        """
        if db_field.name == 'album':
            kwargs['queryset'] = Album.objects.filter(user=request.user)
        return super(ProfileVideoAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


profile.register(Video, ProfileVideoAdmin)


class ProfileUserAdmin(ProfileModelAdmin, UserAdmin):
    list_select_related = True

    list_display = ('username', 'url', 'email', 'top_album', 'is_staff', )
    list_filter = ()

    fieldsets = (
        ('Account info', {'fields': ('username', 'password', )}),
        ('Personal info', {'fields': ('email', 'first_name', 'last_name', )}),
        ('Viewer info', {'fields': ('url', 'top_album', 'cache_size', 'cache_archive_size', 'cache_info', )}),
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
        Show in drop down menu only user albums
        """
        if db_field.name == 'top_album':
            kwargs['queryset'] = Album.objects.filter(user=request.user)
        return super(ProfileUserAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


profile.register(ProxyUser, ProfileUserAdmin)