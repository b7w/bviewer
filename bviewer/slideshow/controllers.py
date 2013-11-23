# -*- coding: utf-8 -*-
import logging
import random
import math
import uuid

from django.core.paginator import Paginator
import django_rq

from bviewer.core.models import Image


logger = logging.getLogger(__name__)


class SlideShowController(object):
    PER_PAGE = 64

    @staticmethod
    def new_key():
        return uuid.uuid1().hex

    def __init__(self, slideshow_id):
        self.key = slideshow_id
        self.redis = django_rq.get_connection()

    def generate_new(self, ratio=0.5):
        assert 0 < ratio < 1
        if not self.key:
            self.key = self.new_key()

        def mapper(pages_count, page_number):
            x = math.pi / pages_count * page_number
            return 3.0 / 4 * math.sin(x + math.pi / 2) + 1

        paginator = Paginator(Image.objects.all(), self.PER_PAGE)
        for i in paginator.page_range:
            items = paginator.page(i).object_list
            popularity = mapper(paginator.num_pages, i - 1)
            random_per_page = int(self.PER_PAGE * ratio * popularity)
            images = random.sample(items, random_per_page)
            self.redis.sadd(self.key, *[i.id for i in images])

        return self.key

    def is_empty(self):
        return not (self.key and self.redis.scard(self.key))

    def next_image_id(self):
        return self.redis.spop(self.key)
