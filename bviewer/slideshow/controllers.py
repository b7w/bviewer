# -*- coding: utf-8 -*-
import logging
import random
import math

from django.core.paginator import Paginator
import django_rq

from bviewer.core.models import Image


logger = logging.getLogger(__name__)


class SlideShowController(object):
    PER_PAGE = 64
    SLIDE_SHOW_KEY = 'slideshow'

    def get_key(self, gallery_id):
        return 'slideshow-id:' + self.session.session_key + ':' + gallery_id

    def __init__(self, session):
        self.session = session
        self._data = session.get(self.SLIDE_SHOW_KEY) or {}
        self._redis = django_rq.get_connection()

    def _generate_new(self, key, ratio=0.5):
        assert 0 < ratio < 1

        def mapper(pages_count, page_number):
            x = math.pi / pages_count * page_number
            return 3.0 / 4 * math.sin(x + math.pi / 2) + 1

        paginator = Paginator(Image.objects.all(), self.PER_PAGE)
        for i in paginator.page_range:
            items = paginator.page(i).object_list
            popularity = mapper(paginator.num_pages, i - 1)
            random_per_page = int(self.PER_PAGE * ratio * popularity)
            images = random.sample(items, random_per_page)
            self._redis.sadd(key, *[i.id for i in images])

    def safe_create(self, gallery_id):
        key = self.get_key(gallery_id)
        if not self._redis.scard(key):
            self._generate_new(key)

    def list(self):
        return list(self._data.itervalues())

    def get(self, gallery_id):
        slideshow = self._data.get(gallery_id)
        if slideshow:
            self.safe_create(gallery_id)
            return slideshow

    def next_image_id(self, gallery_id):
        key = self.get_key(gallery_id)
        return self._redis.spop(key)

    def add(self, slideshow):
        self._data[slideshow.gallery_id] = slideshow
        self.safe_create(slideshow.gallery_id)
        self.save()

    def delete(self, gallery_id):
        del self._data[gallery_id]
        self._redis.delete(self.get_key(gallery_id))
        self.save()

    def save(self):
        self.session[self.SLIDE_SHOW_KEY] = self._data
