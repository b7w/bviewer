# -*- coding: utf-8 -*-
import os

from django.test import TestCase
from django.conf import settings
from mock import Mock

from bviewer.core import settings as settings_local
from bviewer.core.exceptions import FileError
from bviewer.core.files.storage import ImageStorage, ImagePath, ImageFolder


class FileTest(TestCase):
    f1 = ImagePath(Mock(), '1.jpg')
    f2 = ImagePath(Mock(), '2.jpg')

    def test_file(self):
        self.assertEqual(self.f1.name, '1.jpg')
        self.assertEqual(self.f1.path, 'root/p1/1.jpg')
        self.assertEqual(self.f1.saved, False)

    def test_order(self):
        self.assertLess(self.f1, self.f2)

        l = [self.f2, self.f1]
        l2 = [self.f1, self.f2]
        self.assertEqual(sorted(l), l2)


class FolderTest(TestCase):
    def test_spit(self):
        res = ImageFolder('root/p1', []).split_path
        ref = [
            ('root', 'root'),
            ('p1', 'root/p1'),
        ]
        self.assertEqual(res, ref)


class StorageTest(TestCase):
    def setUp(self):
        self.data = ['1.jpg', '2.jpg', '3.jpg', '4.jpeg', '5.jpg']
        for i in self.data:
            with open(os.path.join(settings.TMP_PATH, i), 'w') as f:
                f.write('test')
        self.VIEWER_STORAGE_PATH = settings_local.VIEWER_STORAGE_PATH
        settings_local.VIEWER_STORAGE_PATH = settings.PROJECT_PATH
        self.test_dir = os.path.join(settings.TMP_PATH, 'test')
        if not os.path.exists(self.test_dir):
            os.mkdir(self.test_dir)

        holder = Mock(home='tmp', url='tmp')
        self.storage = ImageStorage(holder)

    def tearDown(self):
        settings_local.VIEWER_STORAGE_PATH = self.VIEWER_STORAGE_PATH
        if os.path.exists(self.test_dir):
            os.removedirs(self.test_dir)
        for i in self.data:
            os.remove(os.path.join(settings.TMP_PATH, i))

    def test_list(self):
        out = self.storage.list('')
        self.assertEqual([i.path for i in out.dirs], ['test'])
        self.assertEqual(out.back, '')
        self.assertEqual([i.path for i in out.files], self.data)

        out = self.storage.list('test')
        self.assertEqual(out.dirs, [])
        self.assertEqual(out.back, '')
        self.assertEqual(out.files, [])

    def test_exists(self):
        self.assertRaises(FileError, self.storage.list, 'root')

    def test_path(self):
        """
        Test path path inject to look throw higher directories
        """
        self.assertRaises(FileError, self.storage.list, '../')
        self.assertRaises(FileError, self.storage.list, '/')
        self.assertRaises(FileError, self.storage.list, './')
        self.assertRaises(FileError, self.storage.list, '.test')
        self.assertRaises(FileError, self.storage.list, 'test/.')
        self.assertRaises(FileError, self.storage.list, 'test/../../')
