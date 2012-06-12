# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils import simplejson
from bviewer.archive.controls import ZipArchive, ZipArchiveTask
from bviewer.core.files.serve import DownloadResponse
from bviewer.core.models import Gallery, Image
from bviewer.core.utils import get_gallery_user

import logging

logger = logging.getLogger(__name__)


def Archive( request, id, user=None ):
    """
    Start to archive images, or if done redirect to download
    js - waite while done, after redirect to download
    """
    holder, user_url = get_gallery_user(request, user)
    if not holder:
        raise Http404("No user defined")

    main = Gallery.objects.safe_get(id=id, user__id=holder.id)
    if not main:
        raise Http404("No gallery found")

    images = Image.objects.filter(gallery__user__id=holder.id, gallery=id)
    z = ZipArchiveTask(images, holder.home, holder.url)

    # links for redirect to download, and check status
    redirect = reverse("archive.download", kwargs={"user": user_url, "id": id, "hash": z.hash})
    link = reverse("archive.status", kwargs={"user": user_url, "id": id, "hash": z.hash})

    if z.status(holder.url, z.hash) == "DONE":
        return HttpResponseRedirect(redirect)
    z.process()
    return render(request, "archive/download.html", {
        'path': request.path,
        'link': link,
        'redirect': redirect,
        'gallery': main,
        'back': True,
        'user_url': user_url,
        })


def ArchiveStatus( request, id, hash, user=None ):
    """
    Check if archive exists and ready for download
    """
    holder, user_url = get_gallery_user(request, user)
    if not holder:
        raise Http404("No user defined")

    status = ZipArchive.status(holder.url, hash)
    data = {"status": status, "gallery": id, "id": hash}

    return HttpResponse(simplejson.dumps(data))


def Download( request, id, hash, user=None ):
    """
    Download archive
    """
    holder, user_url = get_gallery_user(request, user)
    if not holder:
        raise Http404("No user defined")

    main = Gallery.objects.safe_get(id=id, user__id=holder.id)
    if not main:
        raise Http404("No gallery found")

    if ZipArchive.status(holder.url, hash) == "NONE":
        raise Http404("No file found")

    logger.info("download archive '%s'", main.title)
    url = ZipArchive.url(holder.url, hash)
    name = u"{0} - {1}.zip".format(main.time.strftime("%Y-%m-%d"), main.title)
    return DownloadResponse.build(url, name)