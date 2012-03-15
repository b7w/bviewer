# -*- coding: utf-8 -*-

from django.contrib.auth.models import User, Permission

from core.models import ProxyUser, Gallery


class TestData:
    def __init__(self):
        self.user_b7w = None

    def loadAll(self):
        self.loadUsers( )
        self.loadGalleries( )

    def loadUsers(self):
        self.user_b7w = ProxyUser( username="B7W" )
        self.user_b7w.set_password( "pass" )
        self.user_b7w.save( )
        self.userSetHolder( "B7W" )

    def userSetHolder(self, name):
        b7w = User.objects.get( username=name )
        perm = Permission.objects.get( codename="user_holder" )
        b7w.user_permissions.add( perm )
        b7w.save( )


    def loadGalleries(self):
        top = self.user_b7w.top_gallery
        self.gallery_year = Gallery( parent=top, user=self.user_b7w, title="Happy new Year" )
        self.gallery_year.description = "Happy new Year description"
        self.gallery_year.save( )

        self.gallery_month = Gallery( parent=top, user=self.user_b7w, title="Happy new month" )
        self.gallery_month.description = "Happy new month description"
        self.gallery_month.save( )

        self.gallery_other = Gallery( parent=top, user=self.user_b7w, title="Other" )
        self.gallery_other.description = "Other description"
        self.gallery_other.save( )

        self.gallery_other = Gallery( parent=self.gallery_other, user=self.user_b7w, title="Old" )
        self.gallery_other.description = "Old description"
        self.gallery_other.save( )

        self.gallery_other = Gallery( user=self.user_b7w, title="Hidden" )
        self.gallery_other.description = "Hidden description"
        self.gallery_other.save( )