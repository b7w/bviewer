# -*- coding: utf-8 -*-

from celery.task import task
from bviewer.archive.controls import ZipArchive


@task
def cache_archive( *args, **kwargs ):
    """
    Create :class:`~bviewer.archive.controls.ZipArchive` and run `process`

    :rtype: bool
    """
    archive = ZipArchive(*args, **kwargs)
    archive.process()
    return True