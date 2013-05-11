# -*- coding: utf-8 -*-
import logging

from django.contrib.auth.decorators import login_required, permission_required
from django.http import Http404
from django.shortcuts import render

from bviewer.core.controllers import get_gallery_user, GalleryController
from bviewer.core.exceptions import FileError
from bviewer.core.files import Storage
from bviewer.core.files.response import download_response
from bviewer.core.images import CacheImage
from bviewer.core.utils import ResizeOptions, as_job
from bviewer.core.views import message_view


logger = logging.getLogger(__name__)


@login_required
@permission_required('core.user_holder')
def images_view(request, uid):
    holder = get_gallery_user(request)
    if not holder:
        raise Http404()

    controller = GalleryController(holder, request.user, uid)
    main = controller.get_object()
    if not main:
        return message_view(request, message='No such gallery')

    images = controller.get_images()
    storage = Storage(holder.home, images)
    folder = storage.list(request.GET.get('p', ''))
    return render(request, 'profile/images.html', {
        'gallery': main,
        'folder': folder,
    })


@login_required
@permission_required('core.user_holder')
def download_image(request):
    if request.GET.get('p', None):
        path = request.GET['p']
        user = get_gallery_user(request)
        storage = Storage(user.home)
        try:
            if storage.exists(path):
                options = ResizeOptions.from_settings(user, 'tiny')
                image = CacheImage(path, options)
                if not image.is_exists():
                    as_job(image.process)
                name = Storage.name(path)
                return download_response(image.url, name)
            raise Http404('No such file')
        except FileError as e:
            raise Http404(e)

    raise Http404('No Image')