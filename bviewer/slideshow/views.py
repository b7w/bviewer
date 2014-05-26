# -*- coding: utf-8 -*-
import logging
from django.core.urlresolvers import reverse
from django.shortcuts import render

from bviewer.core.controllers import get_gallery_user, GalleryController
from bviewer.core.views import message_view


logger = logging.getLogger(__name__)


def index_view(request):
    """
    Slideshow, create new for each session
    """
    holder = get_gallery_user(request)
    if not holder:
        return message_view(request, message='No user defined')

    controller = GalleryController(holder, request.user, uid=holder.top_gallery_id)
    if not controller.exists():
        return message_view(request, message='No such gallery')

    main = controller.get_object()
    link = reverse('actions-slideshow-get-or-create') + '?gallery={0}'.format(holder.top_gallery_id)
    return render(request, 'slideshow/index.html', {
        'holder': holder,
        'main': main,
        'link': link,
        'back': dict(gallery_id=main.id, home=holder.top_gallery_id == main.id),
    })


def gallery_view(request, gallery_id):
    """
    Slideshow, create new for each session
    """
    holder = get_gallery_user(request)
    if not holder:
        return message_view(request, message='No user defined')

    controller = GalleryController(holder, request.user, uid=gallery_id)
    if not controller.exists():
        return message_view(request, message='No such gallery')

    main = controller.get_object()
    link = reverse('actions-slideshow-get-or-create') + '?gallery={0}'.format(gallery_id)
    return render(request, 'slideshow/index.html', {
        'holder': holder,
        'main': main,
        'link': link,
        'back': dict(gallery_id=main.id, home=holder.top_gallery_id == main.id),
    })