# -*- coding: utf-8 -*-
from datetime import datetime
import json
import logging
import uuid

try:
    from urllib2 import urlopen, URLError
except ImportError:
    from urllib.request import urlopen
    from urllib.error import URLError

from django.contrib.auth.models import User, AbstractUser, Permission
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.query_utils import Q
from django.db.models.signals import post_save
from django.utils.encoding import smart_text
from django.utils.html import escape

from bviewer.core.files.storage import ImageStorage
from bviewer.core.exceptions import HttpError, ViewerError

logger = logging.getLogger(__name__)


def uuid_pk(length=10):
    """
    Return function that generate uuid1 and cut it to `length`.
    UUID default size is 32 chars.
    """

    def _uuid_pk():
        return uuid.uuid1().hex[:length]

    return _uuid_pk


class ProxyManager(models.Manager):
    """
    Adds safe_get, that return obj or none
    """

    def safe_get(self, *args, **kwargs):
        try:
            return self.get(*args, **kwargs)
        except self.model.DoesNotExist:
            return None


class ProxyUser(User):
    CACHE_SIZE_MIN = 16
    CACHE_SIZE_MAX = 256
    CACHE_ARCHIVE_SIZE_MIN = 128
    CACHE_ARCHIVE_SIZE_MAX = 2048

    url = models.CharField(max_length=16, unique=True)
    home = models.CharField(max_length=256, blank=True, default='')

    cache_size = models.PositiveIntegerField(default=32,
        validators=[MinValueValidator(CACHE_SIZE_MIN), MaxValueValidator(CACHE_SIZE_MAX)])
    cache_archive_size = models.PositiveIntegerField(default=256,
        validators=[MinValueValidator(CACHE_ARCHIVE_SIZE_MIN), MaxValueValidator(CACHE_ARCHIVE_SIZE_MAX)])

    top_gallery = models.ForeignKey('Gallery', related_name='top', null=True, blank=True, on_delete=models.DO_NOTHING)
    about_title = models.CharField(max_length=256, blank=True)
    about_text = models.TextField(max_length=1024, blank=True)

    objects = ProxyManager()

    def save(self, *args, **kwargs):
        if not self.url:
            url = self.username.lower()
            domain = Site.objects.get_current().domain
            self.url = '{0}.{1}'.format(url, domain)
        super(ProxyUser, self).save(*args, **kwargs)

    def __eq__(self, other):
        """
        if isinstance of ProxyUser, AbstractUser:
            return self.id == other.id
        return False
        """
        if other and isinstance(other, (ProxyUser, AbstractUser)):
            return self.id == other.id
        return False

    class Meta(object):
        db_table = 'core_profile'
        ordering = ['username']
        verbose_name = 'Gallery user'
        verbose_name_plural = 'Gallery users'
        permissions = (
            ('user_holder', 'User is galleries holder'),
        )


def add_top_gallery(sender, instance, created, **kwargs):
    if created:
        gal = Gallery(user=instance, title='Welcome', description='Edit main gallery to change it')
        gal.save()
        instance.top_gallery = gal
        perms = Permission.objects.filter(
            Q(codename='change_proxyuser') |
            Q(codename='user_holder') |
            Q(codename='add_gallery') |
            Q(codename='change_gallery') |
            Q(codename='delete_gallery') |
            Q(codename='add_image') |
            Q(codename='change_image') |
            Q(codename='delete_image') |
            Q(codename='add_video') |
            Q(codename='change_video') |
            Q(codename='delete_video')
        )
        instance.user_permissions = list(perms)
        instance.save()


post_save.connect(add_top_gallery, sender=ProxyUser)


class Gallery(models.Model):
    VISIBLE = 1
    HIDDEN = 2
    PRIVATE = 3
    VISIBILITY_CHOICE = ((VISIBLE, 'Visible'), (HIDDEN, 'Hidden'), (PRIVATE, 'Private'),)

    id = models.CharField(max_length=32, default=uuid_pk(length=8), primary_key=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.SET_NULL)
    title = models.CharField(max_length=256)
    user = models.ForeignKey(ProxyUser)
    visibility = models.SmallIntegerField(max_length=1, choices=VISIBILITY_CHOICE, default=VISIBLE)
    description = models.TextField(max_length=512, null=True, blank=True)
    thumbnail = models.ForeignKey('Image', null=True, blank=True, related_name='thumbnail', on_delete=models.SET_NULL)
    time = models.DateTimeField(default=datetime.now)

    objects = ProxyManager()

    def __str__(self):
        if self.parent:
            return smart_text('{0} -> {1}').format(self.title, self.parent)
        return self.title

    __unicode__ = __str__

    class Meta(object):
        verbose_name = 'Gallery'
        verbose_name_plural = 'Galleries'
        ordering = ['-time']
        unique_together = (('title', 'user'),)


class Image(models.Model):
    id = models.CharField(max_length=32, default=uuid_pk(length=12), primary_key=True)
    gallery = models.ForeignKey(Gallery)
    path = models.CharField(max_length=256)
    time = models.DateTimeField(default=datetime.now)

    objects = ProxyManager()

    def clean(self):
        """
        Check path exists
        """
        storage = ImageStorage(self.gallery.user)
        if not storage.exists(self.path):
            raise ValidationError('No {0} path exists'.format(self.path))

    def __str__(self):
        return smart_text('{0}: {1}').format(self.gallery.title, self.path)

    __unicode__ = __str__

    class Meta(object):
        verbose_name = 'Image'
        ordering = ['time']
        unique_together = (('gallery', 'path'),)


def update_time_from_exif(sender, instance, created, **kwargs):
    """
    :type instance: Image
    """
    if created:
        storage = ImageStorage(instance.gallery.user)
        image_path = storage.get_path(instance.path)
        if image_path.exists and image_path.exif.ctime:
            instance.time = image_path.exif.ctime
            instance.save()


post_save.connect(update_time_from_exif, sender=Image)


class Video(models.Model):
    VIMIO = 1
    YOUTUBE = 2
    TYPE_CHOICE = ((YOUTUBE, 'YouTube'), (VIMIO, 'Vimio'),)

    id = models.CharField(max_length=32, default=uuid_pk(length=12), primary_key=True)
    uid = models.CharField(max_length=32)
    type = models.SmallIntegerField(max_length=1, choices=TYPE_CHOICE, default=YOUTUBE)
    gallery = models.ForeignKey(Gallery)
    title = models.CharField(max_length=256)
    description = models.TextField(max_length=512, null=True, blank=True)
    time = models.DateTimeField(default=datetime.now)

    objects = ProxyManager()

    @property
    def url(self):
        """
        Build escaped url to video
        """
        if self.type == self.VIMIO:
            return escape('http://player.vimeo.com/video/{0}?title=0'.format(self.uid))
        elif self.type == self.YOUTUBE:
            return escape('http://youtube.com/embed/{0}'.format(self.uid))
        raise ValueError('unknown video type: {0}'.format(self.type))

    @property
    def thumbnail_url(self):
        """
        Get video thumbnail url.
        """
        if self.type == self.VIMIO:
            try:
                url = 'http://vimeo.com/api/v2/video/{0}.json'.format(self.uid)
                raw = urlopen(url, timeout=4).read()
                info = json.loads(raw, encoding='UTF-8').pop()
                return info['thumbnail_large']
            except URLError as e:
                logger.exception('Error urlopen VIMIO api')
                raise HttpError(e)
        elif self.type == self.YOUTUBE:
            return 'http://img.youtube.com/vi/{0}/hqdefault.jpg'.format(self.uid)
        raise ViewerError('Unknown video type: {0}'.format(self.type))

    def __str__(self):
        return self.title

    __unicode__ = __str__

    class Meta(object):
        verbose_name = 'Video'
        ordering = ['time']
        unique_together = (('uid', 'gallery'),)
