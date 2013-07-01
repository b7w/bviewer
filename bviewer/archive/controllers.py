# -*- coding: utf-8 -*-
import logging

from django_rq import get_queue

from bviewer.core.files.storage import ImageStorage
from bviewer.core.utils import ResizeOptions, cache_method


logger = logging.getLogger(__name__)


class ZipArchiveController(object):
    def __init__(self, image_paths, holder, name=None):
        """
        :type image_paths: list of str
        :type holder: bviewer.core.models.ProxyUser
        :type name: str
        """
        self.holder = holder
        self.storage = ImageStorage(holder)
        self.image_paths = [self.storage.get_path(i) for i in image_paths]
        self.name = name or self.uid

        options = ResizeOptions(name=self.name)
        self.archive = self.storage.get_archive(options)

        self.url = self.archive.url

    @property
    def status(self):
        """
        Return status DONE, PROCESSING, NONE

        :rtype: str
        """
        #TODO: No way to check FS is archive creating
        if self.archive.cache_exists:
            return 'DONE'
        elif self.archive.cache_exists:
            return 'PROCESSING'
        return 'NONE'

    @property
    @cache_method
    def uid(self):
        pack = [self.holder.home, ]
        for path in self.image_paths:
            pack.append(path.cache_name)
        return self.storage.hash_for(tuple(pack))

    @property
    def progress(self):
        """
        Progress in range of 0..100

        :rtype: int
        """
        if self.status == 'DONE':
            return 100
        if self.status == 'PROCESSING':
            done = self.archive.cache_ctime

            f = lambda path: self.storage.get_path(path).ctime
            real = sum(f(i.path) for i in self.image_paths)
            return int(float(done) / real * 100)
        if self.status == 'NONE':
            return 0

    def process(self):
        """
        Process if `self.status` == NONE
        """
        if self.status == 'NONE':
            with self.archive.cache_open() as z:
                for image_path in self.image_paths:
                    with image_path.open(mode='rb') as f:
                        z.writestr(image_path.name, f.read())

            self.archive.rename_temp_cache()

    def add_job(self):
        """
        Send task to RQ `low` queue
        """
        rq = get_queue(name='low')
        rq.enqueue(self.process)
