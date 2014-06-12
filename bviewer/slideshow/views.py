# -*- coding: utf-8 -*-
import logging
from django.core.urlresolvers import reverse
from django.shortcuts import render

from bviewer.core.controllers import get_album_user, AlbumController
from bviewer.core.views import message_view


logger = logging.getLogger(__name__)


def index_view(request):
    """
    Slideshow, create new for each session
    """
    holder = get_album_user(request)
    if not holder:
        return message_view(request, message='No user defined')

    controller = AlbumController(holder, request.user, uid=holder.top_album_id)
    if not controller.exists():
        return message_view(request, message='No such album')

    main = controller.get_object()
    link = reverse('actions-slideshow-get-or-create') + '?album={0}'.format(holder.top_album_id)
    return render(request, 'slideshow/index.html', {
        'holder': holder,
        'main': main,
        'link': link,
        'back': dict(album_id=main.id, home=holder.top_album_id == main.id),
    })


def album_view(request, album_id):
    """
    Slideshow, create new for each session
    """
    holder = get_album_user(request)
    if not holder:
        return message_view(request, message='No user defined')

    controller = AlbumController(holder, request.user, uid=album_id)
    if not controller.exists():
        return message_view(request, message='No such album')

    main = controller.get_object()
    link = reverse('actions-slideshow-get-or-create') + '?album={0}'.format(album_id)
    return render(request, 'slideshow/index.html', {
        'holder': holder,
        'main': main,
        'link': link,
        'back': dict(album_id=main.id, home=holder.top_album_id == main.id),
    })