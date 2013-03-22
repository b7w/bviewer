# -*- coding: utf-8 -*-

from django_rq import job

from bviewer.archive.controls import ZipArchive


@job
def cache_archive(*args, **kwargs):
    """
    Create :class:`~bviewer.archive.controls.ZipArchive` and run `process`

    :rtype: bool
    """
    archive = ZipArchive(*args, **kwargs)
    archive.process()
    return True