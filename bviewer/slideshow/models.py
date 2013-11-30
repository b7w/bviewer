# -*- coding: utf-8 -*-
from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone
from django.utils.encoding import smart_text

from bviewer.core.models import Gallery, ProxyManager, uuid_pk


class SlideShow(models.Model):
    NEW = 1
    BUILD = 2
    FINISHED = 3
    STATUS_CHOICE = ((NEW, 'New'), (BUILD, 'Build'), (FINISHED, 'Finished'),)

    id = models.CharField(max_length=32, default=uuid_pk(length=8), primary_key=True)
    gallery = models.ForeignKey(Gallery, on_delete=models.DO_NOTHING)
    session_key = models.CharField(max_length=32)
    timer = models.SmallIntegerField(max_length=4, default=10)
    status = models.SmallIntegerField(max_length=1, choices=STATUS_CHOICE, default=NEW)
    image_count = models.IntegerField(max_length=8, default=0)
    time = models.DateTimeField(default=timezone.now)

    objects = ProxyManager()

    def __str__(self):
        return smart_text('{0}: {1}').format(self.gallery.title, self.status)

    __unicode__ = __str__

    class Meta(object):
        verbose_name = 'SlideShow'
        ordering = ['time']


def generate_slideshow_async(sender, instance, created, **kwargs):
    from bviewer.slideshow.controllers import SlideShowGenerator

    if created:
        controller = SlideShowGenerator(instance)
        controller.generate_async()


post_save.connect(generate_slideshow_async, sender=SlideShow)