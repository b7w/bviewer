# -*- coding: utf-8 -*-


class SlideShow(object):
    def __init__(self, gallery_id, timer=10, repeat=True):
        self.gallery_id = gallery_id
        self.timer = timer
        self.repeat = repeat
