# -*- coding: utf-8 -*-
import logging

from django.contrib.auth.decorators import login_required, permission_required
from django.http import Http404
from django.shortcuts import render
from django.utils.encoding import smart_text

from bviewer.core.controllers import get_gallery_user, GalleryController
from bviewer.core.exceptions import FileError
from bviewer.core.files.response import download_response
from bviewer.core.files.storage import ImageStorage
from bviewer.core.files.utils import ImageFolder
from bviewer.core.images import CacheImage
from bviewer.core.utils import ImageOptions, as_job
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

    image_paths = set(i.path for i in controller.get_images(force=True))
    storage = ImageStorage(holder)
    path = request.GET.get('p', '')
    try:
        folder = ImageFolder(path, storage.list(path, image_paths))
    except FileError as e:
        logger.exception(e)
        return message_view(request, message=smart_text(e))
    return render(request, 'profile/images.html', {
        'gallery': main,
        'folder': folder,
        'title': 'Select images',
    })


@login_required
@permission_required('core.user_holder')
def download_image(request):
    if request.GET.get('p', None):
        path = request.GET['p']
        user = get_gallery_user(request)
        storage = ImageStorage(user)
        options = ImageOptions.from_settings('tiny')
        image_path = storage.get_path(path, options)
        try:
            if image_path.exists:
                if not image_path.cache_exists:
                    image = CacheImage(image_path)
                    as_job(image.process)
                return download_response(image_path)
            err_msg = smart_text('Path not exists "{0}"').format(path)
            logger.info(err_msg)
            raise Http404(err_msg)
        except FileError as e:
            logger.info(e)
            raise Http404(e)

    raise Http404('No Image')