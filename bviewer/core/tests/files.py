# -*- coding: utf-8 -*-
import os
from mock import Mock

from django.test import TestCase
from django.conf import settings

from bviewer.core.exceptions import FileError
from bviewer.core.files.storage import ImageStorage, ImagePath, ImageFolder
from bviewer.core.utils import ResizeOptions


class ImagePathTest(TestCase):
    def setUp(self):
        self.storage = Mock(hash_for=str)
        self.f1 = ImagePath(self.storage, 'path/1.jpg')
        self.f2 = ImagePath(self.storage, 'path/2.jpg')

    def test_file(self):
        self.assertEqual(self.f1.name, '1.jpg')
        self.assertEqual(self.f1.path, 'path/1.jpg')
        self.assertEqual(self.f1.saved, False)

    def test_order(self):
        self.assertLess(self.f1, self.f2)

        l = [self.f2, self.f1]
        l2 = [self.f1, self.f2]
        self.assertEqual(sorted(l), l2)

    def test_cache_name_unique(self):
        options = [
            ResizeOptions(32, 32, crop=False, quality=95),
            ResizeOptions(64, 32, crop=False, quality=95),
            ResizeOptions(32, 64, crop=False, quality=95),
            ResizeOptions(32, 32, crop=True, quality=95),
            ResizeOptions(32, 32, crop=False, quality=100),
            ResizeOptions(32, 32, crop=False, quality=100, name='unique_name'),
        ]
        path = 'some/path/img.jpg'

        hashes = set(ImagePath(self.storage, path, i).cache_name for i in options)
        self.assertEqual(len(options), len(hashes), msg='Check unique hashes for different options')

        name1 = ImagePath(self.storage, 'path1', ResizeOptions()).cache_name
        name2 = ImagePath(self.storage, 'path2', ResizeOptions()).cache_name
        self.assertNotEqual(name1, name2)

    def test_cache_name_repeatability(self):
        name1 = ImagePath(self.storage, 'path', ResizeOptions()).cache_name
        name2 = ImagePath(self.storage, 'path', ResizeOptions()).cache_name
        self.assertEqual(name1, name2)


class ImageFolderTest(TestCase):
    def test_spit_path(self):
        res = ImageFolder('root/p1', []).split_path
        ref = [
            ('root', 'root'),
            ('p1', 'root/p1'),
        ]
        self.assertEqual(res, ref)


class StorageTest(TestCase):
    def setUp(self):
        self.data = ['1.jpg', '2.jpeg', '3.jpg', '4.jpg', '5.jpg']
        self.test_dir = settings.VIEWER_CACHE_PATH
        self.test_user_dir = os.path.join(self.test_dir, 'test')

        holder = Mock(home='test', url='test')
        self.storage = ImageStorage(holder, root_path=self.test_dir, cache_path=self.test_dir)
        self.storage.clear_cache()
        os.makedirs(os.path.join(self.test_dir, 'test/folder'))

        for i in self.data:
            with open(os.path.join(self.test_user_dir, i), 'w') as f:
                f.write('test')

    def test_list(self):
        out = self.storage.list()
        self.assertEqual([i.path for i in out if i.is_dir], ['folder'])
        self.assertEqual([i.path for i in out if i.is_image], self.data)

        out = self.storage.list('folder')
        self.assertEqual(out, [])

    def test_exists(self):
        self.assertRaises(FileError, self.storage.list, 'None')

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
