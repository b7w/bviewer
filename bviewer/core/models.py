# -*- coding: utf-8 -*-
import json
import logging
import uuid

try:
    from urllib2 import urlopen, URLError
except ImportError:
    from urllib.request import urlopen
    from urllib.error import URLError

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone
from django.utils.encoding import smart_text
from django.utils.html import escape

from bviewer.core.files.storage import ImageStorage
from bviewer.core.exceptions import HttpError, ViewerError
from bviewer.core.utils import set_time_from_exif


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


class Access(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    gallery = models.ForeignKey('Gallery', on_delete=models.DO_NOTHING)
    is_active = models.BooleanField(default=False)

    objects = ProxyManager()

    def __str__(self):
        return smart_text('{0}: {1}').format(self.user, self.gallery)

    __unicode__ = __str__

    class Meta(object):
        unique_together = (('user', 'gallery'),)


class Gallery(models.Model):
    CACHE_SIZE_MIN = 16
    CACHE_SIZE_MAX = 512
    CACHE_ARCHIVE_SIZE_MIN = 128
    CACHE_ARCHIVE_SIZE_MAX = 2048

    user = models.ForeignKey(User)
    description = models.CharField(max_length=256)

    url = models.CharField(max_length=16, unique=True)
    home = models.CharField(max_length=512, blank=True, default='')

    cache_size = models.PositiveIntegerField(default=32,
                                             validators=[MinValueValidator(CACHE_SIZE_MIN), MaxValueValidator(CACHE_SIZE_MAX)])
    cache_archive_size = models.PositiveIntegerField(default=256,
                                                     validators=[MinValueValidator(CACHE_ARCHIVE_SIZE_MIN),
                                                                 MaxValueValidator(CACHE_ARCHIVE_SIZE_MAX)])

    top_album = models.ForeignKey('Album', related_name='top', null=True, blank=True, on_delete=models.DO_NOTHING)
    about_title = models.CharField(max_length=256, blank=True)
    about_text = models.TextField(max_length=1024, blank=True)

    objects = ProxyManager()

    def save(self, *args, **kwargs):
        if not self.url:
            url = self.user.username.lower()
            domain = Site.objects.get_current().domain
            self.url = '{0}.{1}'.format(url, domain)
        super(Gallery, self).save(*args, **kwargs)

    def __str__(self):
        return self.url

    __unicode__ = __str__

    class Meta(object):
        ordering = ['user']
        verbose_name = 'Gallery'
        verbose_name_plural = 'Galleries'
        permissions = (
            ('user_holder', 'User is gallery holder'),
        )


def add_top_album(sender, instance, created, **kwargs):
    if created:
        instance.top_album = Album.objects \
            .create(gallery=instance, title='Welcome', description='Edit main album to change it')
        instance.save()


post_save.connect(add_top_album, sender=Gallery)


def date_now():
    return timezone.now().replace(minute=0, second=0, microsecond=0)


class Album(models.Model):
    VISIBLE = 1
    HIDDEN = 2
    PRIVATE = 3
    VISIBILITY_CHOICE = ((VISIBLE, 'Visible'), (HIDDEN, 'Hidden'), (PRIVATE, 'Private'),)

    ASK = 1
    DESK = 2
    SORT_CHOICE = ((ASK, 'Ascending '), (DESK, 'Descending'), )

    id = models.CharField(max_length=32, default=uuid_pk(length=8), primary_key=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.SET_NULL)
    title = models.CharField(max_length=256)
    gallery = models.ForeignKey(Gallery)
    visibility = models.SmallIntegerField(max_length=1, choices=VISIBILITY_CHOICE, default=VISIBLE,
                                          help_text='HIDDEN - not shown on page for anonymous, '
                                                    'PRIVATE - available only to the gallery')
    album_sorting = models.SmallIntegerField(max_length=1, choices=SORT_CHOICE, default=ASK,
                                             help_text='How to sort albums inside')
    allow_archiving = models.BooleanField(default=True)
    description = models.TextField(max_length=512, null=True, blank=True)
    thumbnail = models.ForeignKey('Image', null=True, blank=True, related_name='thumbnail', on_delete=models.SET_NULL)
    time = models.DateTimeField(default=date_now)

    objects = ProxyManager()

    def __str__(self):
        if self.parent:
            return smart_text('{0} -> {1}').format(self.title, self.parent)
        return self.title

    __unicode__ = __str__

    class Meta(object):
        verbose_name = 'Album'
        verbose_name_plural = 'Albums'
        ordering = ['-time']
        unique_together = (('title', 'gallery'),)


class Image(models.Model):
    id = models.CharField(max_length=32, default=uuid_pk(length=12), primary_key=True)
    album = models.ForeignKey(Album)
    path = models.CharField(max_length=512)
    time = models.DateTimeField(default=timezone.now)

    objects = ProxyManager()

    def clean(self):
        """
        Check path exists
        """
        storage = ImageStorage(self.album.gallery)
        if not storage.exists(self.path):
            raise ValidationError(smart_text('No {0} path exists').format(self.path))

    def __str__(self):
        return smart_text('{0}: {1}').format(self.album.title, self.path)

    __unicode__ = __str__

    class Meta(object):
        verbose_name = 'Image'
        ordering = ['time']
        unique_together = (('album', 'path'),)


def update_time_from_exif(sender, instance, created, **kwargs):
    """
    :type instance: Image
    """
    if created:
        storage = ImageStorage(instance.album.gallery)
        set_time_from_exif(storage, instance, save=True)


post_save.connect(update_time_from_exif, sender=Image)


class Video(models.Model):
    VIMIO = 1
    YOUTUBE = 2
    TYPE_CHOICE = ((YOUTUBE, 'YouTube'), (VIMIO, 'Vimio'),)

    id = models.CharField(max_length=32, default=uuid_pk(length=12), primary_key=True)
    uid = models.CharField(max_length=32)
    type = models.SmallIntegerField(max_length=1, choices=TYPE_CHOICE, default=YOUTUBE)
    album = models.ForeignKey(Album)
    title = models.CharField(max_length=256)
    description = models.TextField(max_length=512, null=True, blank=True)
    time = models.DateTimeField(default=timezone.now)

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
        raise ValueError(smart_text('unknown video type: {0}').format(self.type))

    @property
    def thumbnail_url(self):
        """
        Get video thumbnail url.
        """
        if self.type == self.VIMIO:
            try:
                url = 'http://vimeo.com/api/v2/video/{0}.json'.format(self.uid)
                raw = urlopen(url, timeout=4).read()
                info = json.loads(smart_text(raw), encoding='UTF-8').pop()
                return info['thumbnail_large']
            except URLError as e:
                logger.exception('Error urlopen VIMIO api')
                raise HttpError(e)
        elif self.type == self.YOUTUBE:
            return 'http://img.youtube.com/vi/{0}/hqdefault.jpg'.format(self.uid)
        raise ViewerError(smart_text('Unknown video type: {0}').format(self.type))

    def __str__(self):
        return self.title

    __unicode__ = __str__

    class Meta(object):
        verbose_name = 'Video'
        ordering = ['time']
        unique_together = (('uid', 'album'),)
