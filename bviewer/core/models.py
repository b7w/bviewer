# -*- coding: utf-8 -*-

from datetime import datetime
from collections import deque
import urllib2

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.query_utils import Q
from django.db.models.signals import post_save
from django.utils.html import escape
from django.utils import simplejson


class ProxyManager(models.Manager):
    """
    Adds safe_get, that return obj or none
    """

    def safe_get(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None


class ProxyUser(User):
    url = models.CharField(max_length=16, unique=True)
    home = models.CharField(max_length=256, null=True, blank=True)
    cache_size = models.PositiveIntegerField(default=32, validators=[MinValueValidator(16), MaxValueValidator(256)])
    top_gallery = models.ForeignKey('Gallery', related_name='top', null=True, blank=True)
    about_title = models.CharField(max_length=256, blank=True)
    about_text = models.TextField(max_length=1024, blank=True)
    avatar = models.ForeignKey('Image', related_name='avatar', null=True, blank=True)

    objects = ProxyManager()

    def for_json(self):
        data = {
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'is_staff': self.is_staff,
            'is_superuser': self.is_superuser,
            'last_login': self.last_login,
            'date_joined': self.date_joined,
            'profile': {
                'avatar': self.avatar_id,
                'about_text': self.about_text,
                'about_title': self.about_title,
            }
        }
        return data

    def save(self, force_insert=False, force_update=False, using=None):
        if not self.url:
            self.url = self.username.lower()
        super(ProxyUser, self).save(force_insert, force_update, using)

    def __eq__(self, other):
        if other and other.is_authenticated():
            return self.id == other.id
        return False


    class Meta:
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
        instance.save()

post_save.connect(add_top_gallery, sender=ProxyUser)


class Gallery(models.Model):
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')
    title = models.CharField(max_length=256)
    user = models.ForeignKey(ProxyUser)
    private = models.BooleanField(default=False)
    description = models.TextField(max_length=512, null=True, blank=True)
    thumbnail = models.ForeignKey('Image', null=True, blank=True, related_name='thumbnail')
    time = models.DateTimeField(default=datetime.now)

    objects = ProxyManager()

    @classmethod
    def get_galleries(cls, top_id, private=None):
        """
        :type top_id: int
        :type private: bool
        :rtype: (Gallery, list of Gallery)
        """
        if private is not None:
            query = Gallery.objects.filter(Q(private=private), Q(id=top_id) | Q(parent=top_id))
        else:
            query = Gallery.objects.filter(Q(id=top_id) | Q(parent=top_id))
        if not len(query):
            return None, []
        main = None
        galleries = []
        for item in query:
            if item.id == top_id:
                main = item
            else:
                galleries.append(item)
        return main, galleries

    @classmethod
    def as_tree(cls, user):
        """
        :type user: django.contrib.auth.models.User
        :rtype: GalleryTree
        """
        objects = Gallery.objects.filter(user=user)
        return GalleryTree.make(objects)

    def is_child_of(self, parent_id):
        """
        Check if self is child of parent_id

        :type parent_id: int
        :rtype: bool
        """
        objects = deque(Gallery.objects.filter(parent=parent_id))
        ids = deque()
        while len(objects):
            obj = objects.popleft()
            if obj.id == self.id:
                return True
            ids.append(obj.id)
            if not len(objects) and len(ids):
                objects.extend(Gallery.objects.filter(parent=ids.popleft()))
        return False

    def for_json(self):
        data = {
            'id': self.id,
            'title': self.title,
            'private': self.private,
            'description': self.description,
            'time': self.time,
        }
        if self.thumbnail:
            data['thumbnail'] = self.thumbnail_id
        return data

    def __unicode__(self):
        if self.parent:
            return self.title + u' -> ' + unicode(self.parent)
        return self.title

    class Meta:
        verbose_name = 'Gallery'
        verbose_name_plural = 'Galleries'
        ordering = ['-time']
        unique_together = (('title', 'user'),)


class GalleryTree:
    """
    Class to represent list of `bviewer.core.models.Gallery` as a tree
    """

    def __init__(self, value, objects):
        """
        :type value: bviewer.core.models.Gallery
        :type objects: list of bviewer.core.models.Gallery
        """
        self.value = value
        self._gen = (GalleryTree(i, objects) for i in objects if i.parent_id == value.id)
        self._children = None

    @property
    def children(self):
        if not self._children:
            self._children = list(self._gen)
        return self._children

    @property
    def has_children(self):
        return bool(len(self.children))

    @classmethod
    def make(cls, objects):
        """
        Convert Models list to list of GalleryTree

        :type objects: list of bviewer.core.models.Gallery
        :rtype: list of GalleryTree
        """
        return [GalleryTree(i, objects) for i in objects if i.parent_id is None]

    def __str__(self):
        return 'GalleryTree{{v={0}}}'.format(self.value)


class Image(models.Model):
    gallery = models.ForeignKey(Gallery)
    path = models.CharField(max_length=256)

    objects = ProxyManager()

    def for_json(self):
        data = {
            'id': self.id,
            'gallery': self.gallery_id,
            'path': self.path,
        }
        return data

    def __unicode__(self):
        return unicode(self.gallery.title) + u': ' + self.path

    class Meta:
        ordering = ['path']
        unique_together = (('gallery', 'path'),)


class Video(models.Model):
    VIMIO = 1
    YOUTUBE = 2
    TYPE_CHOICE = ((YOUTUBE, 'YouTube'), (VIMIO, 'Vimio'),)

    uid = models.CharField(max_length=32)
    type = models.SmallIntegerField(max_length=1, choices=TYPE_CHOICE)
    gallery = models.ForeignKey(Gallery)
    title = models.CharField(max_length=256)
    description = models.TextField(max_length=512, null=True, blank=True)

    objects = ProxyManager()

    def for_json(self):
        data = {
            'id': self.id,
            'uid': self.uid,
            'type': self.type,
            'gallery': self.gallery_id,
            'title': self.title,
            'description': self.description,
        }
        return data

    @property
    def url(self):
        """
        Build escaped url to video
        """
        if self.type == self.VIMIO:
            return escape('http://player.vimeo.com/video/{0}'.format(self.uid))
        elif self.type == self.YOUTUBE:
            return escape('http://youtube.com/embed/{0}'.format(self.uid))
        raise ValueError('unknown video type: {0}'.format(self.type))


    @property
    def thumbnail_url(self):
        """
        Get video thumbnail url.
        """
        if self.type == self.VIMIO:
            url = 'http://vimeo.com/api/v2/video/{0}.json'.format(self.uid)
            json = urllib2.urlopen(url).read()
            info = simplejson.loads(json, encoding='UTF-8').pop()
            return info['thumbnail_large']
        elif self.type == self.YOUTUBE:
            return 'http://img.youtube.com/vi/{0}/hqdefault.jpg'.format(self.uid)
        raise ValueError('unknown video type: {0}'.format(self.type))

    def __unicode__(self):
        return self.title

    class Meta:
        unique_together = (('uid', 'gallery'),)
