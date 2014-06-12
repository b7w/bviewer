# -*- coding: utf-8 -*-
import json
import logging
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils.encoding import smart_text

from bviewer.archive.controllers import ZipArchiveController
from bviewer.core.controllers import get_album_user, AlbumController
from bviewer.core.files.response import download_response
from bviewer.core.views import message_view


logger = logging.getLogger(__name__)

NO_USER_DEFINED = 'No user defined'
NO_GALLERY_FOUND = 'No album found'
NOT_ALBUM = 'It is not album with images'
NOT_ALLOW_ARCHIVING = 'Archiving is disabled for this album'


def index_view(request, gid):
    """
    Start to archive images, or if done redirect to download
    js - waite while done, after redirect to download
    """
    holder = get_album_user(request)
    if not holder:
        return message_view(request, message=NO_USER_DEFINED)

    controller = AlbumController(holder, request.user, uid=gid)
    if not controller.exists():
        return message_view(request, message=NO_GALLERY_FOUND)

    if not controller.is_album():
        return message_view(request, message=NOT_ALBUM)

    if not controller.is_archiving_allowed():
        return message_view(request, message=NOT_ALLOW_ARCHIVING)

    image_paths = [i.path for i in controller.get_images()]
    z = ZipArchiveController(image_paths, holder)

    # links for redirect to download, and check status
    redirect = reverse('archive.download', kwargs=dict(gid=gid, uid=z.uid))
    link = reverse('archive.status', kwargs=dict(gid=gid, uid=z.uid))
    main = controller.get_object()

    if z.status == 'DONE':
        return HttpResponseRedirect(redirect)

    z.add_job()
    return render(request, 'archive/download.html', {
        'holder': holder,
        'path': request.path,
        'link': link,
        'redirect': redirect,
        'album': main,
        'back': dict(album_id=main.id),
    })


def status_view(request, gid, uid):
    """
    Check if archive exists and ready for download
    """
    holder = get_album_user(request)
    if not holder:
        raise Http404(NO_USER_DEFINED)

    controller = AlbumController(holder, request.user, gid)
    if not controller.exists():
        return HttpResponse(json.dumps(dict(error=NO_GALLERY_FOUND)))

    if not controller.is_album():
        return HttpResponse(json.dumps(dict(error=NOT_ALBUM)))

    if not controller.is_archiving_allowed():
        return HttpResponse(json.dumps(dict(error=NOT_ALLOW_ARCHIVING)))

    image_paths = [i.path for i in controller.get_images()]
    z = ZipArchiveController(image_paths, holder, name=uid)
    data = dict(status=z.status, album=gid, uid=uid, progress=z.progress)

    return HttpResponse(json.dumps(data))


def download_view(request, gid, uid):
    """
    Download archive
    """
    holder = get_album_user(request)
    if not holder:
        raise Http404(NO_USER_DEFINED)

    controller = AlbumController(holder, request.user, uid=gid)
    if not controller.exists():
        raise Http404(NO_GALLERY_FOUND)

    if not controller.is_album():
        return message_view(request, message=NOT_ALBUM)

    if not controller.is_archiving_allowed():
        return message_view(request, message=NOT_ALLOW_ARCHIVING)

    image_paths = [i.path for i in controller.get_images()]
    z = ZipArchiveController(image_paths, holder, name=uid)

    if z == 'NONE':
        raise Http404('No file found')

    main = controller.get_object()
    logger.info(smart_text('download archive "%s"'), main.title)
    name = smart_text('{0} - {1}.zip').format(main.time.strftime('%Y-%m-%d'), main.title)
    return download_response(z.archive, name=name)