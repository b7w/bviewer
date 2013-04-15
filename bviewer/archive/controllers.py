# -*- coding: utf-8 -*-
import os
import zipfile
import logging

from bviewer.core import settings
from bviewer.core.files import Storage
from bviewer.core.utils import FileUniqueName


logger = logging.getLogger(__name__)


class ZipArchiveController(object):
    """
    Zip images

    :type images: Image
    :type storage: string
    """

    def __init__(self, images, storage, user):
        self.images = images
        self.storage = storage
        self.user = user
        self._hash = None

    @property
    def hash(self):
        """
        Build unique name for set if path images

        :rtype: string
        """
        if not self._hash:
            self.hash_builder = FileUniqueName()
            slice = ';'.join([i.path for i in self.images])
            self._hash = self.hash_builder.build(slice)
        return self._hash

    @classmethod
    def url(cls, user, hash):
        """
        Get utl for download via unique name

        :type user: string
        :type hash: string
        :rtype: string
        """
        return os.path.join(user, '{0}.zip'.format(hash))

    @classmethod
    def file_name(cls, user, hash, part=False):
        """
        Return full path fot `hash` name and `user`, if `part` add '.part' to the end

        :type user: string
        :type hash: string
        :type part: bool # some
        :rtype: string
        """
        path = os.path.join(settings.VIEWER_CACHE_PATH, user)
        if not os.path.exists(path):
            os.mkdir(path)
        if part:
            return os.path.join(path, '{0}.zip.part'.format(hash))
        return os.path.join(path, '{0}.zip'.format(hash))

    @classmethod
    def status(cls, user, hash):
        """
        Return status DONE, PROCESSING, NONE in strings
        where `user` - username

        :type user: string
        :type hash: string
        :rtype: string
        """
        if os.path.exists(cls.file_name(user, hash)):
            return 'DONE'
        elif os.path.exists(cls.file_name(user, hash, part=True)):
            return 'PROCESSING'
        return 'NONE'

    def process(self):
        """
        Process if `self.status` == NONE
        """
        cache_tmp = self.file_name(self.user, self.hash, part=True)
        cache = self.file_name(self.user, self.hash)

        if self.status(self.user, self.hash) == 'NONE':
            with open(cache_tmp, mode='wb') as f:
                with zipfile.ZipFile(f, 'w', zipfile.ZIP_DEFLATED) as z:
                    for image in self.images:
                        path = os.path.join(settings.VIEWER_STORAGE_PATH, self.storage, image.path)
                        z.write(path, Storage.name(image.path))

            os.rename(cache_tmp, cache)
        return True
