# -*- coding: utf-8 -*-
import logging

from bviewer.core.files.storage import ImageStorage
from bviewer.core.utils import ImageOptions, cache_method, as_job, get_redis_connection


logger = logging.getLogger(__name__)


class ZipArchiveController(object):
    STATUS_KEY_TIMOUT = 4 * 60

    def __init__(self, image_paths, holder, name=None):
        """
        :type image_paths: list of str
        :type holder: bviewer.core.models.ProxyUser
        :type name: str
        """
        self.holder = holder
        self.storage = ImageStorage(holder, archive_cache=True)
        self.image_paths = [self.storage.get_path(i) for i in image_paths]
        self.name = name or self.uid

        options = ImageOptions(name=self.name)
        self.archive = self.storage.get_archive(options)

    @property
    def status(self):
        """
        Return status DONE, PROCESSING, NONE

        :rtype: str
        """
        if self.archive.cache_exists:
            return 'DONE'
        if 0 <= self.progress <= 100:
            return 'PROCESSING'
        return 'NONE'

    @property
    @cache_method
    def uid(self):
        pack = [self.holder.home, ]
        for path in self.image_paths:
            if path.exists:
                pack.append(path.cache_name)
        return self.storage.hash_for(tuple(pack))

    @property
    def _redis_uid(self):
        return 'bviewer.archive.status:{0}'.format(self.uid)

    @property
    def progress(self):
        """
        Get progress from redis. Range 0..100, if None return -1.

        :rtype: int
        """
        redis = get_redis_connection()
        value = redis.get(self._redis_uid)
        return int(value) if value is not None else -1

    def process(self):
        """
        Process if `self.status` == NONE
        Update redis progress each file.
        """
        # local otherwise not pickle
        redis = get_redis_connection()

        if self.status == 'NONE':
            with self.archive.open(mode='w') as z:
                for i, image_path in enumerate(self.image_paths, start=1):
                    # if file not exists - ignore
                    if image_path.exists:
                        with image_path.open(mode='rb') as f:
                            z.writestr(image_path.name, f.read())

                    percent = int(float(i) / len(self.image_paths) * 100)
                    redis.setex(key=self._redis_uid, value=percent, time=self.STATUS_KEY_TIMOUT)

            self.archive.rename_temp_cache()

    def add_job(self):
        """
        Send task to RQ `low` queue
        """
        as_job(self.process, queue='low', waite=False)