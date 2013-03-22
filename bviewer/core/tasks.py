# -*- coding: utf-8 -*-

from django_rq import job


@job
def cache_image_process(image):
    image.process()
    return image


@job
def cache_image_download(image):
    image.download()
    return image