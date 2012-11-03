# -*- coding: utf-8 -*-
from datetime import datetime
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
    top_gallery = models.ForeignKey("Gallery", related_name="top", null=True, blank=True)
    about_title = models.CharField(max_length=256, blank=True)
    about_text = models.TextField(max_length=1024, blank=True)
    avatar = models.ForeignKey("Image", related_name="avatar", null=True, blank=True)

    objects = ProxyManager()

    def for_json(self):
        data = {
            "username": self.username,
            "email": self.email,
            "is_active": self.is_active,
            "is_staff": self.is_staff,
            "is_superuser": self.is_superuser,
            "last_login": self.last_login,
            "date_joined": self.date_joined,
            "profile": {
                "avatar": self.avatar_id,
                "about_text": self.about_text,
                "about_title": self.about_title,
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
        db_table = "core_profile"
        ordering = ["username"]
        verbose_name = "Gallery user"
        verbose_name_plural = "Gallery users"
        permissions = (
            ("user_holder", "User is galleries holder"),
            )


def add_top_gallery(sender, instance, created, **kwargs):
    if created:
        gal = Gallery(user=instance, title="Welcome", description="Edit main gallery to change it")
        gal.save()
        instance.top_gallery = gal
        instance.save()

post_save.connect(add_top_gallery, sender=ProxyUser)


class Gallery(models.Model):
    parent = models.ForeignKey("self", null=True, blank=True, related_name="children")
    title = models.CharField(max_length=256)
    user = models.ForeignKey(ProxyUser)
    private = models.BooleanField(default=False)
    description = models.TextField(max_length=512, null=True, blank=True)
    thumbnail = models.ForeignKey("Image", null=True, blank=True, related_name="thumbnail")
    time = models.DateTimeField(default=datetime.now)

    objects = ProxyManager()

    @classmethod
    def get_galleries(cls, top_id, private=None):
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

    def for_json(self):
        data = {
            "id": self.id,
            "title": self.title,
            "private": self.private,
            "description": self.description,
            "time": self.time,
        }
        if self.thumbnail:
            data["thumbnail"] = self.thumbnail_id
        return data

    def __unicode__(self):
        if self.parent:
            return self.title + u" -> " + unicode(self.parent)
        return self.title

    class Meta:
        verbose_name = "Gallery"
        verbose_name_plural = "Galleries"
        ordering = ["-time"]
        unique_together = (("title", "user"),)


class Image(models.Model):
    gallery = models.ForeignKey(Gallery)
    path = models.CharField(max_length=256)

    objects = ProxyManager()

    def for_json(self):
        data = {
            "id": self.id,
            "gallery": self.gallery_id,
            "path": self.path,
        }
        return data

    def __unicode__(self):
        return unicode(self.gallery.title) + u": " + self.path

    class Meta:
        ordering = ["path"]
        unique_together = (("gallery", "path"),)


class Video(models.Model):
    uid = models.CharField(max_length=32)
    gallery = models.ForeignKey(Gallery)
    title = models.CharField(max_length=256)
    description = models.TextField(max_length=512, null=True, blank=True)

    objects = ProxyManager()

    def for_json(self):
        data = {
            "id": self.id,
            "uid": self.uid,
            "gallery": self.gallery_id,
            "title": self.title,
            "description": self.description,
        }
        return data

    @property
    def url(self):
        """
        Build escaped url to video
        """
        return escape("http://player.vimeo.com/video/" + self.uid)

    @property
    def thumbnail_url(self):
        """
        Get video thumbnail url.
        """
        url = "http://vimeo.com/api/v2/video/{0}.json".format(self.uid)
        json = urllib2.urlopen(url).read()
        info = simplejson.loads(json, encoding="UTF-8").pop()
        return info["thumbnail_large"]

    def __unicode__(self):
        return self.title

    class Meta:
        unique_together = (("uid", "gallery"),)
