# -*- coding: utf-8 -*-
import logging
import random


logger = logging.getLogger(__name__)


class SlideShowController(object):
    IMAGES = ['fb6f6662edf9', '46e91f44e331', '8645b4f2bb06', '86a9071ebb06', '882da16cbb06', '88c9a76abb06',
              '46e91f44e331', '46e91f44e331',
              'a329f276445a', 'a329f276445a']

    def __init__(self, slideshow_id):
        self.slideshow_id = slideshow_id

    @property
    def status(self):
        return True

    def next_image_id(self):
        return random.choice(self.IMAGES)