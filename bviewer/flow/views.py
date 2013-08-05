# -*- coding: utf-8 -*-
from django.http import Http404
from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie

from bviewer.core.controllers import get_gallery_user, GalleryController
from bviewer.core.files.storage import ImageStorage
from bviewer.core.views import message_view
from bviewer.flow.utils import FlowCollection


@cache_page(60 * 60)
@vary_on_cookie
def gallery_view(request, uid):
    """
    Show sub galleries or images with videos
    """
    holder = get_gallery_user(request)
    if not holder:
        return message_view(request, message='No user defined')

    controller = GalleryController(holder, request.user, uid)
    main = controller.get_object()
    if not main:
        return message_view(request, message='No such gallery')
    galleries = controller.get_galleries()

    template = 'flow/gallery.html' if controller.is_album() else 'core/galleries.html'

    return render(request, template, {
        'main': main,
        'galleries': galleries,
        'back': dict(gallery_id=main.parent_id, home=holder.top_gallery_id == main.parent_id),
    })


@cache_page(60 * 60)
@vary_on_cookie
def flow_view(request, uid):
    """
    Show sub galleries or images with videos
    """
    holder = get_gallery_user(request)
    if not holder:
        return message_view(request, message='No user defined')

    controller = GalleryController(holder, request.user, uid)
    main = controller.get_object()
    if not main:
        raise Http404('No such gallery')
    images = controller.get_images()
    storage = ImageStorage(holder)

    width = int(request.GET.get('width'))
    margin = int(request.GET.get('margin').replace('px', ''))
    flow = FlowCollection(width, 400, margin * 2)
    flow.add(images)

    return render(request, 'flow/flow.html', {
        'flow': flow,
    })