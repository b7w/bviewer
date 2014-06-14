# -*- coding: utf-8 -*-
import hashlib
import uuid

from django.utils.encoding import smart_bytes


class BaseImageStorage(object):
    def hash_for(self, content):
        return hashlib.sha1(smart_bytes(content)).hexdigest()

    def gen_temp_name(self):
        return uuid.uuid1().hex