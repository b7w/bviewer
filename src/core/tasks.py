# -*- coding: utf-8 -*-
from celery.decorators import periodic_task, task
from celery.schedules import crontab

from core import settings
from core.management.commands.clearcache import ClearCache


@periodic_task( run_every=crontab( **settings.VIEWER_CLEAR ) )
def clear_cache():
    cache = ClearCache( path=settings.VIEWER_CACHE_PATH )
    cache.clear( )


@task
def cache_image_process( image ):
    image.process( )
    return image


@task
def cache_image_download( image ):
    image.download( )
    return image