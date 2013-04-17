# -*- coding: utf-8 -*-
import os
import zipfile
import logging

from django_rq import get_queue

from bviewer.core import settings
from bviewer.core.files import Storage
from bviewer.core.utils import FileUniqueName, cache_method


logger = logging.getLogger(__name__)


class ZipArchiveController(object):
    def __init__(self, images, holder, uid=None):
        """
        :type images: bviewer.core.models.Image
        :type holder: bviewer.core.models.ProxyUser
        :type uid: str
        """
        self.images = images
        self.holder = holder
        self.default_uid = uid

    def _archive_path(self, part=False):
        """
        Return abs archive path, if `part` add '.part' to the end.

        :type part: bool
        :rtype: str
        """
        path = os.path.join(settings.VIEWER_CACHE_PATH, self.holder.url)
        if not os.path.exists(path):
            os.mkdir(path)
        if part:
            return os.path.join(path, '{0}.zip.part'.format(self.uid))
        return os.path.join(path, '{0}.zip'.format(self.uid))

    def _image_path(self, image):
        """
        Abs path to image

        :type image: bviewer.core.models.Image
        :rtype: str
        """
        return os.path.join(settings.VIEWER_STORAGE_PATH, self.holder.home, image.path)

    @property
    @cache_method
    def uid(self):
        """
        :rtype: str
        """
        if self.default_uid:
            return self.default_uid
        builder = FileUniqueName()
        name = ';'.join(self._image_path(i) for i in self.images)
        return builder.build(name)

    @property
    def url(self):
        """
        Get utl for download via unique name
        """
        return os.path.join(self.holder.url, '{0}.zip'.format(self.uid))

    @property
    def status(self):
        """
        Return status DONE, PROCESSING, NONE

        :rtype: str
        """
        if os.path.exists(self._archive_path()):
            return 'DONE'
        elif os.path.exists(self._archive_path(part=True)):
            return 'PROCESSING'
        return 'NONE'

    @property
    def progress(self):
        """
        Progress in range of 0..100

        :return: int
        """
        if self.status == 'DONE':
            return 100
        if self.status == 'PROCESSING':
            fname = self._archive_path(part=True)
            done = os.path.getsize(fname)
            real = sum(os.path.getsize(self._image_path(i)) for i in self.images)
            return int(float(done) / real * 100)
        if self.status == 'NONE':
            return 0

    def process(self):
        """
        Process if `self.status` == NONE
        """
        cache_tmp = self._archive_path(part=True)
        cache = self._archive_path()
        if self.status == 'NONE':
            with open(cache_tmp, mode='wb') as f:
                with zipfile.ZipFile(f, 'w', zipfile.ZIP_DEFLATED) as z:
                    for image in self.images:
                        z.write(self._image_path(image), Storage.name(image.path))

            os.rename(cache_tmp, cache)
        return True

    def add_job(self):
        """
        Send task to RQ `low` queue
        """
        rq = get_queue(name='low')
        rq.enqueue(self.process)
