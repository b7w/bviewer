# -*- coding: utf-8 -*-

import os

from django.test import TestCase
from django.conf import settings

from bviewer.core import settings as settings_local
from bviewer.core.files import Storage

class StorageTest( TestCase ):
    def setUp(self):
        self.data = ["1.jpg", "2.jpg", "3.jpg", "4.jpeg", "5.jpg"]
        for i in self.data:
            with open( os.path.join( settings.TMP_PATH, i ), 'w' ) as f:
                f.write( "test" )
        self.VIEWER_STORAGE_PATH = settings_local.VIEWER_STORAGE_PATH
        settings_local.VIEWER_STORAGE_PATH = settings.PROJECT_PATH
        self.test_dir = os.path.join( settings.TMP_PATH, "test" )
        if not os.path.exists( self.test_dir ):
            os.mkdir( self.test_dir )

        self.storage = Storage( "tmp" )

    def tearDown(self):
        settings_local.VIEWER_STORAGE_PATH = self.VIEWER_STORAGE_PATH
        if os.path.exists( self.test_dir ):
            os.removedirs( self.test_dir )
        for i in self.data:
            os.remove( os.path.join( settings.TMP_PATH, i ) )

    def test_list(self):
        out = self.storage.list( "" )
        out["files"].sort( )
        assert out["dirs"] == ["test"]
        assert out["back"] == ''
        assert out["files"] == self.data

        out = self.storage.list( "test" )
        assert out["dirs"] == []
        assert out["back"] == ''
        assert out["files"] == []

    def test_exists(self):
        self.assertRaises( IOError, self.storage.list, "root" )

    def test_path(self):
        """
        Test path path inject to look throw higher directories
        """
        self.assertRaises( IOError, self.storage.list, "../" )
        self.assertRaises( IOError, self.storage.list, "/" )
        self.assertRaises( IOError, self.storage.list, "./" )
        self.assertRaises( IOError, self.storage.list, ".test" )
        self.assertRaises( IOError, self.storage.list, "test/." )
        self.assertRaises( IOError, self.storage.list, "test/../../" )

    def test_name(self):
        assert Storage.name( "tmp/some name.jpg" ) == "some name.jpg"