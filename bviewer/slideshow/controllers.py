# -*- coding: utf-8 -*-
import logging
import random
import math

from django.db.models import Q
from django.core.paginator import Paginator
import django_rq

from bviewer.core.models import Image
from bviewer.core.utils import as_job
from bviewer.slideshow.models import SlideShow


logger = logging.getLogger(__name__)


class SlideShowGenerator(object):
    PER_PAGE = 64

    def __init__(self, slideshow):
        self._redis = django_rq.get_connection()
        self.slideshow = slideshow

    def get_key(self):
        return 'slideshow-id:' + self.slideshow.id

    def generate(self, ratio=0.5):
        assert 0 < ratio < 1

        def mapper(pages_count, page_number):
            x = math.pi / pages_count * page_number
            return 3.0 / 4 * math.sin(x + math.pi / 2) + 1

        queryset = Image.objects.filter(gallery=self.slideshow.gallery)
        paginator = Paginator(queryset, self.PER_PAGE)
        for i in paginator.page_range:
            items = paginator.page(i).object_list
            popularity = mapper(paginator.num_pages, i - 1)
            random_per_page = int(self.PER_PAGE * ratio * popularity)
            random_per_page = random_per_page if random_per_page <= len(items) else len(items)
            images = random.sample(items, random_per_page)
            self._redis.sadd(self.get_key(), *[i.id for i in images])

        self.slideshow.status = SlideShow.BUILD
        self.slideshow.image_count = self._redis.scard(self.get_key())
        self.slideshow.save()

    def generate_async(self):
        as_job(self.generate, waite=False)


class SlideShowController(object):
    def __init__(self, session_key, slideshow_id=None, gallery_id=None):
        self.session_key = session_key
        self.gallery_id = gallery_id
        self.slideshow_id = slideshow_id
        args = (slideshow_id, gallery_id,)
        assert any(args) and not all(args), 'Need one of slideshow_id/gallery_id kwargs'
        if slideshow_id:
            self.slideshow = SlideShow.objects.safe_get(id=slideshow_id)
        self._redis = django_rq.get_connection()

    def get_key(self):
        return 'slideshow-id:' + self.slideshow.id

    def is_exists(self):
        """
        Work only if `slideshow_id` parameter specified
        """
        return bool(self.slideshow)

    def get_or_create(self):
        status = Q(status=SlideShow.NEW) | Q(status=SlideShow.BUILD)
        items = list(SlideShow.objects.filter(Q(gallery=self.gallery_id), Q(session_key=self.session_key), status))
        for slideshow in items:
            if slideshow.status == SlideShow.BUILD:
                return slideshow
        for slideshow in items:
            if slideshow.status == SlideShow.NEW:
                return slideshow
        return SlideShow.objects.create(session_key=self.session_key, gallery_id=self.gallery_id)

    def next_image(self):
        image_id = self._redis.spop(self.get_key())
        if not image_id:
            return None
        try:
            return Image.objects.select_related().get(id=image_id)
        except Image.DoesNotExist:
            return None

    def finish(self):
        """
        Set FINISHED status for slideshow
        """
        self.slideshow.status = SlideShow.FINISHED
        self.slideshow.save()