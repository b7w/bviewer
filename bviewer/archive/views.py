# -*- coding: utf-8 -*-
import json

import logging

from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils.encoding import smart_text

from bviewer.archive.controllers import ZipArchiveController
from bviewer.core.files.serve import DownloadResponse
from bviewer.core.models import Gallery, Image
from bviewer.core.utils import get_gallery_user, as_job


logger = logging.getLogger(__name__)


def Archive(request, id):
    """
    Start to archive images, or if done redirect to download
    js - waite while done, after redirect to download
    """
    holder = get_gallery_user(request)
    if not holder:
        raise Http404('No user defined')

    main = Gallery.objects.safe_get(id=id, user__id=holder.id)
    if not main:
        raise Http404('No gallery found')

    images = Image.objects.filter(gallery__user__id=holder.id, gallery=id)
    z = ZipArchiveController(images, holder.home, holder.url)

    # links for redirect to download, and check status
    redirect = reverse('archive.download', kwargs=dict(id=id, hash=z.hash))
    link = reverse('archive.status', kwargs=dict(id=id, hash=z.hash))

    if z.status(holder.url, z.hash) == 'DONE':
        return HttpResponseRedirect(redirect)

    as_job(z.process)
    return render(request, 'archive/download.html', {
        'path': request.path,
        'link': link,
        'redirect': redirect,
        'gallery': main,
        'back': True,
    })


def ArchiveStatus(request, id, hash):
    """
    Check if archive exists and ready for download
    """
    holder = get_gallery_user(request)
    if not holder:
        raise Http404('No user defined')

    status = ZipArchiveController.status(holder.url, hash)
    data = dict(status=status, gallery=id, id=hash)

    return HttpResponse(json.dumps(data))


def Download(request, id, hash):
    """
    Download archive
    """
    holder = get_gallery_user(request)
    if not holder:
        raise Http404('No user defined')

    main = Gallery.objects.safe_get(id=id, user__id=holder.id)
    if not main:
        raise Http404('No gallery found')

    if ZipArchiveController.status(holder.url, hash) == 'NONE':
        raise Http404('No file found')

    logger.info(smart_text('download archive "%s"'), main.title)
    url = ZipArchiveController.url(holder.url, hash)
    name = smart_text('{0} - {1}.zip').format(main.time.strftime('%Y-%m-%d'), main.title)
    return DownloadResponse.build(url, name)