# -*- coding: utf-8 -*-
import json
import logging
from django.core.urlresolvers import reverse

from django.http import Http404, HttpResponse
from django.shortcuts import render

from bviewer.core.controllers import get_gallery_user
from bviewer.core.views import message_view
from bviewer.slideshow.controllers import SlideShowController


logger = logging.getLogger(__name__)


def index_view(request):
    """
    Start to archive images, or if done redirect to download
    js - waite while done, after redirect to download
    """
    holder = get_gallery_user(request)
    if not holder:
        return message_view(request, message='No user defined')

    link = reverse('slideshow.next')

    return render(request, 'slideshow/index.html', {
        'holder': holder,
        'link': link,
        'back': dict(gallery_id=holder.top_gallery_id),
    })


def next_image_view(request):
    """
    Check if archive exists and ready for download
    """
    holder = get_gallery_user(request)
    if not holder:
        raise Http404('No user defined')

    controller = SlideShowController(None)
    link = reverse('core.download', args=('big', controller.next_image_id(),))
    data = dict(next=link)

    return HttpResponse(json.dumps(data))