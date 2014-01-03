# -*- coding: utf-8 -*-
import logging
import random

from django.db.models import Q

from bviewer.core.controllers import GalleryController
from bviewer.core.models import Image, Gallery
from bviewer.core.utils import as_job, cache_method, get_redis_connection
from bviewer.slideshow.models import SlideShow


logger = logging.getLogger(__name__)


class SlideShowGenerator(object):
    PER_PAGE = 64

    def __init__(self, slideshow, redis=None):
        self.slideshow = slideshow
        self.redis = redis or get_redis_connection()
        self.holder = slideshow.gallery.user
        self.user = slideshow.user
        self.gallery_ctrl = GalleryController(self.holder, self.user, slideshow.gallery_id)

    def get_key(self):
        return 'slideshow-id:' + self.slideshow.id

    def generate(self, ratio=0.5):
        assert 0 < ratio < 1

        saved_images_count = 0
        for gallery in self.gallery_ctrl.get_all_sub_galleries(parents=False):
            images_ids = Image.objects.filter(gallery=gallery).values_list('id', flat=True)
            count = int(len(images_ids) * ratio)
            images_ids = random.sample(images_ids, count)
            saved_images_count += len(images_ids)
            if images_ids:
                self.redis.sadd(self.get_key(), *images_ids)

        self.slideshow.status = SlideShow.BUILD
        self.slideshow.image_count = saved_images_count
        self.slideshow.save()

    def generate_async(self):
        as_job(self.generate, waite=False)


class SlideShowController(object):
    def __init__(self, user, session_key, slideshow_id=None, gallery_id=None, redis=None):
        self.user = user if user.is_authenticated() else None
        self.session_key = session_key
        self.gallery_id = gallery_id
        self.redis = redis or get_redis_connection()
        self.slideshow_id = slideshow_id
        args = (slideshow_id, gallery_id,)
        assert any(args) and not all(args), 'Need one of slideshow_id/gallery_id kwargs'

    def get_key(self):
        return 'slideshow-id:' + self.slideshow_id

    @cache_method
    def get_object(self):
        """
        Work only if `slideshow_id` parameter specified
        """
        if self.slideshow_id:
            # session_key grants permissions
            return SlideShow.objects.safe_get(id=self.slideshow_id, session_key=self.session_key)

    @cache_method
    def get_gallery(self):
        obj = None
        if self.user:  # if holder == user
            obj = Gallery.objects.safe_get(id=self.gallery_id, user=self.user)
        if not obj:
            obj = Gallery.objects.safe_get(
                Q(pk=self.gallery_id),
                Q(visibility=Gallery.VISIBLE) | Q(visibility=Gallery.HIDDEN)
            )
        return obj

    def get_or_create(self):
        status = Q(status=SlideShow.NEW) | Q(status=SlideShow.BUILD)
        items = list(SlideShow.objects.filter(Q(gallery=self.gallery_id), Q(session_key=self.session_key), status))
        for slideshow in items:
            if slideshow.status == SlideShow.BUILD:
                return slideshow
        for slideshow in items:
            if slideshow.status == SlideShow.NEW:
                return slideshow
        return SlideShow.objects.create(
            session_key=self.session_key,
            gallery_id=self.gallery_id,
            user=self.user
        )

    def next_image(self):
        image_id = self.redis.spop(self.get_key())
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
        self.get_object().status = SlideShow.FINISHED
        self.get_object().save()