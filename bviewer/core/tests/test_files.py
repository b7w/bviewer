# -*- coding: utf-8 -*-
import os

from mock import Mock, patch
from django.test import TestCase
from django.utils import six

from bviewer.core.exceptions import FileError
from bviewer.core.files.path import ImagePath
from bviewer.core.files.proxy import ProxyImageStorage
from bviewer.core.files.storage import ImageStorage
from bviewer.core.files.utils import ImageFolder
from bviewer.core.tests.base import BaseImageStorageTestCase
from bviewer.core.utils import ImageOptions


class ImagePathTestCase(TestCase):
    def setUp(self):
        self.storage = Mock(gallery=Mock(home='home'), hash_for=str)
        self.f1 = ImagePath(self.storage, 'path/1.jpg')
        self.f2 = ImagePath(self.storage, 'path/2.jpg')

    def test_file(self):
        self.assertEqual(self.f1.name, '1.jpg')
        self.assertEqual(self.f1.path, 'path/1.jpg')
        self.assertEqual(self.f1.saved, False)

    def test_url(self):
        storage = Mock(
            hash_for=Mock(return_value='cache_name'),
            gallery=Mock(home='home', url='gallery.url'),
            type='type'
        )
        self.assertEqual(storage.hash_for(), 'cache_name')
        self.assertEqual(storage.gallery.url, 'gallery.url')

        path = ImagePath(storage, 'path/1.jpg')
        self.assertEqual(path.url, 'type/gallery.url/cache_name.jpg')

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

        gallery = Mock(home='home', url='url', cache_size=0)
        # storage try to create cache folder on init, mock it
        with patch('os.makedirs'):
            storage = ImageStorage(gallery, root_path='root', cache_path='cache')

        assert_method_for_cache('os.path.getctime', storage.ctime, side_effect=str)
        assert_method_for_cache('os.path.exists', storage.exists, side_effect=str)
        open_module = 'builtins.open' if six.PY3 else '__builtin__.open'
        assert_method_for_cache(open_module, storage.open, side_effect=lambda path, mode: str(path))


class ProxyImageStorageTestCase(BaseImageStorageTestCase):
    VALUE = Mock()
    VALUE2 = Mock()

    def setUp(self):
        self.gallery = Mock(home='home;home2', url='gallery_url', cache_size=0)
        self.backend = Mock(
            list=Mock(return_value=self.VALUE),
            get_path=Mock(return_value=self.VALUE),
            get_url=Mock(return_value=self.VALUE),
            get_archive=Mock(return_value=self.VALUE),
            clear_cache=Mock(return_value=self.VALUE),
            cache_size=Mock(return_value=10),
        )
        self.backend2 = Mock(
            list=Mock(return_value=self.VALUE2),
            get_path=Mock(return_value=self.VALUE2),
            clear_cache=Mock(return_value=self.VALUE2),
            cache_size=Mock(return_value=100),
        )
        self.storage = self._build_storage(self.backend, self.backend2)
        self.options = Mock()

    def _build_storage(self, backend, backend2):
        def _provider(conf, *args, **kwargs):
            if conf.home == 'home':
                return backend
            if conf.home == 'home2':
                return backend2
            raise AssertionError('Wrong home')

        return ProxyImageStorage(self.gallery, provider=_provider)

    def test_list(self):
        out = self.storage.list(saved_images=self.options)
        self.assertEqual([i.full_path for i in out if i.is_dir], ['home', 'home2'])

        self.assertEqual(self.storage.list('home', saved_images=self.options), self.VALUE)
        self.backend.list.assert_called_with('', saved_images=self.options)
        self.assertEqual(self.storage.list('home/path', saved_images=self.options), self.VALUE)
        self.backend.list.assert_called_with('path', saved_images=self.options)

        self.assertEqual(self.storage.list('home2', saved_images=self.options), self.VALUE2)
        self.backend2.list.assert_called_with('', saved_images=self.options)
        self.assertEqual(self.storage.list('home2/path2', saved_images=self.options), self.VALUE2)
        self.backend2.list.assert_called_with('path2', saved_images=self.options)

    def test_get_path(self):
        out = self.storage.get_path('home/file', options=self.options)
        self.assertEqual(out, self.VALUE)
        self.backend.get_path.assert_called_with('file', options=self.options)

        out = self.storage.get_path('home2/file2', options=self.options)
        self.assertEqual(out, self.VALUE2)
        self.backend2.get_path.assert_called_with('file2', options=self.options)

    def test_get_url(self):
        out = self.storage.get_url('url', options=self.options)
        self.assertEqual(out, self.VALUE)
        self.backend.get_url.assert_called_with('url', options=self.options)

    def test_get_archive(self):
        out = self.storage.get_archive(options=self.options)
        self.assertEqual(out, self.VALUE)
        self.backend.get_archive.assert_called_with(options=self.options)

    def test_clear_cache(self):
        self.storage.clear_cache(full=True)
        self.backend.clear_cache.assert_called_with(full=True)
        self.backend2.clear_cache.assert_called_with(full=True)

    def test_cache_size(self):
        out = self.storage.cache_size()
        self.assertEqual(out, 110)
        self.backend.cache_size.assert_called_with()
        self.backend2.cache_size.assert_called_with()