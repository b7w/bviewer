# -*- coding: utf-8 -*-
import logging
from django.core.urlresolvers import reverse
from django.shortcuts import render

from bviewer.core.controllers import get_gallery, AlbumController
from bviewer.core.views import message_view


logger = logging.getLogger(__name__)

GALLERY_NOT_FOUND = 'No gallery found'


def index_view(request):
    """
    Slideshow, create new for each session
    """
    gallery = get_gallery(request)
    if not gallery:
        return message_view(request, message=GALLERY_NOT_FOUND)

    controller = AlbumController(gallery, request.user, uid=gallery.top_album_id)
    if not controller.exists():
        return message_view(request, message='No such album')

    main = controller.get_object()
    link = reverse('actions-slideshow-get-or-create') + '?album={0}'.format(gallery.top_album_id)
    return render(request, 'slideshow/index.html', {
        'gallery': gallery,
        'main': main,
        'link': link,
        'back': dict(album_id=main.id, home=gallery.top_album_id == main.id),
    })


def album_view(request, album_id):
    """
    Slideshow, create new for each session
    """
    gallery = get_gallery(request)
    if not gallery:
        return message_view(request, message=GALLERY_NOT_FOUND)

    controller = AlbumController(gallery, request.user, uid=album_id)
    if not controller.exists():
        return message_view(request, message='No such album')

    main = controller.get_object()
    link = reverse('actions-slideshow-get-or-create') + '?album={0}'.format(album_id)
    return render(request, 'slideshow/index.html', {
        'gallery': gallery,
        'main': main,
        'link': link,
        'back': dict(album_id=main.id, home=gallery.top_album_id == main.id),
    })