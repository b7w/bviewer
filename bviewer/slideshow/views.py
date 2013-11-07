# -*- coding: utf-8 -*-
import json
import logging
from django.core.urlresolvers import reverse

from django.http import Http404, HttpResponse
from django.shortcuts import render

from bviewer.core.controllers import get_gallery_user
from bviewer.core.views import message_view
from bviewer.slideshow.controllers import SlideShowController
from bviewer.core.models import Image


logger = logging.getLogger(__name__)


def index_view(request):
    """
    Slideshow, create new for each session
    """
    holder = get_gallery_user(request)
    if not holder:
        return message_view(request, message='No user defined')

    uid = request.session.get('slideshow-id')
    controller = SlideShowController(uid)
    if controller.is_empty():
        request.session['slideshow-id'] = controller.generate_new()

    link = reverse('slideshow.next')
    return render(request, 'slideshow/index.html', {
        'holder': holder,
        'link': link,
        'back': dict(gallery_id=holder.top_gallery_id),
    })


def next_image_view(request):
    """
    Next image, return json with link to image and title of gallery.
    If no slideshow create new for each session.
    """
    holder = get_gallery_user(request)
    if not holder:
        raise Http404('No user defined')

    uid = request.session.get('slideshow-id')
    controller = SlideShowController(uid)
    if controller.is_empty():
        controller.generate_new()
        request.session['slideshow-id'] = controller.generate_new()

    image_id = controller.next_image_id()
    image = Image.objects.select_related().get(id=image_id)
    link = reverse('core.download', args=('big', image_id,))
    data = dict(next=link, title=image.gallery.title)
    return HttpResponse(json.dumps(data))
