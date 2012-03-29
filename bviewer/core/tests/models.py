# -*- coding: utf-8 -*-
from django.contrib.auth.models import User

from django.test import TestCase

from bviewer.core.models import ProxyUser, Gallery

class ModelTest( TestCase ):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_new_gallery_user(self):
        """
        Tests domain match
        """
        ProxyUser.objects.create( username="Test", password="secret" )
        assert User.objects.filter( username="Test" ).exists( )
        assert ProxyUser.objects.filter( username="Test" ).exists( )
        assert ProxyUser.objects.get( username="Test" ).top_gallery
        assert Gallery.objects.filter( user__username="Test" ).exists( )