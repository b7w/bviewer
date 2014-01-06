# -*- coding: utf-8 -*-
import os
from mock import Mock, patch

from django.test import TestCase
from django.utils import six

from bviewer.core.exceptions import FileError
from bviewer.core.files.path import ImagePath
from bviewer.core.files.storage import ImageStorage
from bviewer.core.files.utils import ImageFolder
from bviewer.core.tests.base import BaseImageStorageTestCase
from bviewer.core.utils import ImageOptions


class ImagePathTestCase(TestCase):
    def setUp(self):
        self.storage = Mock(hash_for=str)
        self.f1 = ImagePath(self.storage, 'path/1.jpg')
        self.f2 = ImagePath(self.storage, 'path/2.jpg')

    def test_file(self):
        self.assertEqual(self.f1.name, '1.jpg')
        self.assertEqual(self.f1.path, 'path/1.jpg')
        self.assertEqual(self.f1.saved, False)

    def test_url(self):
        storage = Mock(
            hash_for=Mock(return_value='cache_name'),
            holder=Mock(url='holder.url'),
            type='type'
        )
        self.assertEqual(storage.hash_for(), 'cache_name')
        self.assertEqual(storage.holder.url, 'holder.url')

        path = ImagePath(storage, 'path/1.jpg')
        self.assertEqual(path.url, 'type/holder.url/cache_name.jpg')

    def test_order(self):
        self.assertLess(self.f1, self.f2)

        l = [self.f2, self.f1]
        l2 = [self.f1, self.f2]
        self.assertEqual(sorted(l), l2)

    def test_cache_name_unique(self):
        options = [
            ImageOptions(32, 32, crop=False, quality=95),
            ImageOptions(64, 32, crop=False, quality=95),
            ImageOptions(32, 64, crop=False, quality=95),
            ImageOptions(32, 32, crop=True, quality=95),
            ImageOptions(32, 32, crop=False, quality=100),
            ImageOptions(32, 32, crop=False, quality=100, name='unique_name'),
        ]
        path = 'some/path/img.jpg'

        hashes = set(ImagePath(self.storage, path, i).cache_name for i in options)
        self.assertEqual(len(options), len(hashes), msg='Check unique hashes for different options')

        name1 = ImagePath(self.storage, 'path1', ImageOptions()).cache_name
        name2 = ImagePath(self.storage, 'path2', ImageOptions()).cache_name
        self.assertNotEqual(name1, name2)

    def test_cache_name_repeatability(self):
        name1 = ImagePath(self.storage, 'path', ImageOptions()).cache_name
        name2 = ImagePath(self.storage, 'path', ImageOptions()).cache_name
        self.assertEqual(name1, name2)


class ImageFolderTestCase(TestCase):
    def test_back(self):
        folder = ImageFolder('root/p1', [])
        self.assertEqual(folder.back, 'root')

        folder = ImageFolder('root', [])
        self.assertEqual(folder.back, '')

    def test_spit_path(self):
        res = ImageFolder('root/p1', []).split_path
        ref = [
            ('root', 'root'),
            ('p1', 'root/p1'),
        ]
        self.assertEqual(res, ref)


class ImageStorageTestCase(BaseImageStorageTestCase):
    def setUp(self):
        super(ImageStorageTestCase, self).setUp()
        self.data = ['1.jpg', '2.jpeg', '3.jpg', '4.jpg', '5.jpg']
        os.makedirs(os.path.join(self.storage._abs_root_path, 'folder'))

        for i in self.data:
            with open(os.path.join(self.storage._abs_root_path, i), 'w') as f:
                f.write('test')

    def test_list(self):
        out = self.storage.list()
        self.assertEqual([i.path for i in out if i.is_dir], ['folder'])
        self.assertEqual([i.path for i in out if i.is_image], self.data)

        out = self.storage.list('folder')
        self.assertEqual(out, [])

    def test_list_not_found(self):
        self.assertRaises(FileError, self.storage.list, 'None')

    def test_list_wrong_paths(self):
        """
        Test path path inject to look throw higher directories
        """
        self.assertRaises(FileError, self.storage.list, '../')
        self.assertRaises(FileError, self.storage.list, '/')
        self.assertRaises(FileError, self.storage.list, './')
        self.assertRaises(FileError, self.storage.list, '.test')
        self.assertRaises(FileError, self.storage.list, 'test/.')
        self.assertRaises(FileError, self.storage.list, 'test/../../')

    def test_method_for_cache(self):
        """
        Test that method(path) and method(path, for_cache) retrun right values
        """

        def assert_method_for_cache(patch_module, func, side_effect):
            with patch(patch_module) as mock:
                mock.configure_mock(side_effect=side_effect)
                image_path = os.path.normpath('path/img.jpg')

                for_root = os.path.normcase('root/home/path/img.jpg')
                self.assertEqual(func(image_path, for_cache=False), for_root)

                for_cache = os.path.normcase('cache/images/url/path/img.jpg')
                self.assertEqual(func(image_path, for_cache=True), for_cache)

        holder = Mock(home='home', url='url', cache_size=0)
        storage = ImageStorage(holder, root_path='root', cache_path='cache')

        assert_method_for_cache('os.path.getctime', storage.ctime, side_effect=str)
        assert_method_for_cache('os.path.exists', storage.exists, side_effect=str)
        open_module = 'builtins.open' if six.PY3 else '__builtin__.open'
        assert_method_for_cache(open_module, storage.open, side_effect=lambda path, mode: str(path))