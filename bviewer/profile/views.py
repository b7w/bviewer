# -*- coding: utf-8 -*-
import logging

from django.contrib.auth.decorators import login_required, permission_required
from django.http import Http404
from django.shortcuts import render

from bviewer.core.controllers import get_gallery_user, GalleryController
from bviewer.core.exceptions import FileError
from bviewer.core.files.response import download_response
from bviewer.core.files.storage import ImageFolder, ImageStorage
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

    images = set(i.path for i in controller.get_images())
    storage = ImageStorage(holder)
    path = request.GET.get('p', '')
    folder = ImageFolder(path, storage.list(path, images))
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
        storage = ImageStorage(user)
        options = ResizeOptions.from_settings(user, 'tiny')
        image_path = storage.get_path(path, options)
        try:
            if image_path.exists:
                if not image_path.cache_exists:
                    image = CacheImage(image_path)
                    as_job(image.process)
                return download_response(image_path.url, image_path.name)
            raise Http404('No such file')
        except FileError as e:
            raise Http404(e)

    raise Http404('No Image')