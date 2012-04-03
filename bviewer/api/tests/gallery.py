# -*- coding: utf-8 -*-

from django.test import TestCase

from bviewer.core.models import Gallery
from bviewer.api.tests.data import TestData
from bviewer.api.tests.helpers import ClientJson


class GalleryTest( TestCase ):
    def setUp(self):
        self.client = ClientJson( )
        self.data = TestData( )
        self.data.loadAll( )

    def tearDown(self):
        pass

    def test_get(self):
        """
        Tests JsonGalleryGet
        """
        assert self.client.login( username="B7W", password="pass" )

        id = self.data.gallery_top.id
        res = self.client.get_extra( "api.gallery.get", {"id": id} )
        assert res.status_code == 200
        assert res.json["id"] == id
        assert res.json["title"] == "Welcome"
        assert res.json["description"]
        assert res.json["time"]

        res = self.client.get_extra( "api.gallery.get", {"id": -1} )
        assert res.status_code == 200
        assert "error" in res.json

        res = self.client.get_extra( "api.gallery.get", {"id": str( id )} )
        assert res.status_code == 200
        assert res.json["id"] == id

        res = self.client.get_extra( "api.gallery.get", {"title": "Welcome"} )
        assert res.status_code == 200
        assert res.json["id"] == id

        res = self.client.get_extra( "api.gallery.get", {"title": "Happy new Year"} )
        assert res.status_code == 200
        assert res.json["title"] == "Happy new Year"

        res = self.client.get_extra( "api.gallery.get", {"title": "Happy new month"} )
        assert res.status_code == 200
        assert res.json["title"] == "Happy new month"

    def test_all(self):
        """
        Tests JsonGalleryAll
        """
        assert self.client.login( username="B7W", password="pass" )

        res = self.client.get_extra( "api.gallery.all" )
        assert res.status_code == 200
        all = [i.title for i in Gallery.objects.all( )]
        assert sorted( res.json ) == sorted( all )

    def test_tree(self):
        """
        Tests JsonGalleryTree
        """
        assert self.client.login( username="B7W", password="pass" )

        res = self.client.get_extra( "api.gallery.tree.main" )
        assert res.status_code == 200
        assert len( res.json ) == 2
        # fin in array main tree and separate gallery
        main = [i for i in res.json if i["title"] == "Welcome"].pop( )
        hidden = [i for i in res.json if i["title"] == "Hidden"].pop( )

        assert main["title"] == "Welcome"
        assert hidden["title"] == "Hidden"
        assert len( main["children"] ) == 3

        other = [i for i in main["children"] if i["title"] == "Other"].pop( )

        assert len( other["children"] ) == 1
        old = other["children"].pop( )

        assert old["title"] == "Old"

    def test_add(self):
        """
        Tests JsonGalleryAdd
        """
        assert self.client.login( username="B7W", password="pass" )

        res = self.client.get_extra( "api.gallery.add", {"title": "new"} )
        assert res.status_code == 200
        assert res.json["title"] == "new"
        assert Gallery.objects.safe_get( title="new" )

    def test_update(self):
        """
        Tests JsonGalleryUpdate
        """
        assert self.client.login( username="B7W", password="pass" )
        month = Gallery.objects.get( title="Happy new month" )

        res = self.client.get_extra( "api.gallery.update", {"id": month.id, "title": "New", "description": "New D"} )
        assert res.status_code == 200
        assert "success" in res.json
        new = Gallery.objects.get( id=month.id )
        assert new.title == "New"
        assert new.description == "New D"

        res = self.client.get_extra( "api.gallery.update", {"id": month.id, "thumbnail": 100, "time": "1/2/2001"} )
        assert res.status_code == 200
        assert "success" in res.json
        new = Gallery.objects.get( id=month.id )
        assert new.thumbnail is None
        assert new.time.day == 1
        assert new.time.month == 2
        assert new.time.year == 2001


    def test_child(self):
        """
        Tests JsonGalleryChild
        """
        assert self.client.login( username="B7W", password="pass" )
        year = Gallery.objects.get( title="Happy new Year" )
        month = Gallery.objects.get( title="Happy new month" )
        res = self.client.get_extra( "api.gallery.child.add", {"id": year.id, "child": month.id} )
        assert res.status_code == 200
        assert "success" in res.json
        month = Gallery.objects.get( title="Happy new month" )
        assert month.parent_id == year.id

        res = self.client.get_extra( "api.gallery.child.del", {"id": year.id, "child": month.id} )
        assert res.status_code == 200
        assert "success" in res.json
        month = Gallery.objects.get( title="Happy new month" )
        assert month.parent == None

        res = self.client.get_extra( "api.gallery.child.add", {"id": 10, "child": 10} )
        assert res.status_code == 200
        assert "error" in res.json

        res = self.client.get_extra( "api.gallery.child.add", {"id": -1, "child": 10} )
        assert res.status_code == 200
        assert "error" in res.json

        res = self.client.get_extra( "api.gallery.child.add", {"id": 10, "child": -1} )
        assert res.status_code == 200
        assert "error" in res.json

        top = self.data.user_b7w.top_gallery_id
        res = self.client.get_extra( "api.gallery.child.add", {"id": 10, "child": top} )
        assert res.status_code == 200
        assert "error" in res.json

    def test_remove(self):
        """
        Tests JsonGalleryRemove
        """
        assert self.client.login( username="B7W", password="pass" )

        month = Gallery.objects.get( title="Happy new month" )
        res = self.client.get_extra( "api.gallery.remove", {"id": month.id} )
        assert res.status_code == 200
        assert "success" in res.json
        assert Gallery.objects.safe_get( title="Happy new month" ) is None

        res = self.client.get_extra( "api.gallery.remove", {"id": -1} )
        assert res.status_code == 200
        assert "error" in res.json

    def test_pre_cache(self):
        """
        Tests JsonGalleryPreCache
        """
        #TODO: create test