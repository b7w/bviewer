# -*- coding: utf-8 -*-
from datetime import datetime
import urllib2

from django.contrib.auth.models import User
from django.db import models
from django.db.models.query_utils import Q
from django.utils.html import escape
from django.utils import simplejson


class ProxyManager( models.Manager ):
    """
    Adds safe_get, that return obj or none
    """

    def safe_get(self, **kwargs):
        try:
            return self.get( **kwargs )
        except self.model.DoesNotExist:
            return None


class ProxyUser( User ):
    home = models.CharField( max_length=256, null=True, blank=True )
    top_gallery = models.ForeignKey( "Gallery", related_name="top" )
    about_title = models.CharField( max_length=256, blank=True )
    about_text = models.TextField( max_length=256, blank=True )
    avatar = models.ForeignKey( "Image", related_name="avatar", null=True, blank=True )

    objects = ProxyManager( )

    def for_json(self):
        data = {
            "username": self.username,
            "email": self.username,
            "username": self.email,
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

    class Meta:
        db_table = "core_profile"
        ordering = ["username"]
        verbose_name = "User"
        verbose_name_plural = "Users"
        permissions = (
            ("user.holder", "User is galleries holder"),
            )


class Gallery( models.Model ):
    parent = models.ForeignKey( "self", null=True, blank=True, related_name="children" )
    title = models.CharField( max_length=128, unique=True )
    user = models.ForeignKey( ProxyUser )
    description = models.TextField( max_length=256, null=True, blank=True )
    thumbnail = models.ForeignKey( "Image", null=True, blank=True, related_name="thumbnail" )
    time = models.DateTimeField( default=datetime.now )

    objects = ProxyManager( )

    @classmethod
    def get_galleries(cls, top_id ):
        query = Gallery.objects.filter( Q( id=top_id ) | Q( parent=top_id ) )
        if not len( query ):
            return None, []
        main = None
        galleries = []
        for item in query:
            if item.id == top_id:
                main = item
            else:
                galleries.append( item )
        return main, galleries

    def for_json(self):
        data = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "time": self.time,
            }
        if self.thumbnail:
            data["thumbnail"] = self.thumbnail_id
        return data

    def __unicode__(self):
        if self.parent:
            return self.title + u" -> " + unicode( self.parent )
        return self.title

    class Meta:
        ordering = ["time"]


class Image( models.Model ):
    gallery = models.ForeignKey( Gallery )
    path = models.CharField( max_length=128 )

    objects = ProxyManager( )

    def for_json(self):
        data = {
            "id": self.id,
            "gallery": self.gallery_id,
            "path": self.path,
            }
        return data

    def __unicode__(self):
        return unicode( self.gallery.title ) + u": " + self.path

    class Meta:
        unique_together = (("gallery", "path"),)


class Video( models.Model ):
    uid = models.CharField( max_length=32 )
    gallery = models.ForeignKey( Gallery )
    title = models.CharField( max_length=128 )
    description = models.TextField( max_length=256, null=True, blank=True )

    objects = ProxyManager( )

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
        return escape( "http://player.vimeo.com/video/" + self.uid )

    @property
    def thumbnail_url(self):
        """
        Get video thumbnail url.
        """
        url = "http://vimeo.com/api/v2/video/{0}.json".format( self.uid )
        json = urllib2.urlopen( url ).read( )
        info = simplejson.loads( json, encoding="UTF-8" ).pop( )
        return info["thumbnail_large"]

    def __unicode__(self):
        return self.title

    class Meta:
        unique_together = (("uid", "gallery"),)
