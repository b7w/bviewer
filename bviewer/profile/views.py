# -*- coding: utf-8 -*-
import logging

from django.contrib.auth.decorators import login_required, permission_required
from django.http import Http404
from django.shortcuts import render

from bviewer.core.controllers import get_gallery_user
from bviewer.core.files import Storage
from bviewer.core.files.response import download_response
from bviewer.core.images import CacheImage
from bviewer.core.utils import ResizeOptions, as_job
from bviewer.profile.controllers import ImageController
from bviewer.profile.utils import JSONResponse


logger = logging.getLogger(__name__)


@login_required
@permission_required('core.user_holder')
def images_view(request):
    user = get_gallery_user(request)
    if not user:
        raise Http404()
    return render(request, 'profile/images.html', {})


@login_required
@permission_required('core.user_holder')
def json_storage_view(request):
    user = get_gallery_user(request)
    if not user:
        raise Http404()
    storage = Storage(user.home)
    folder = storage.list(request.GET.get('p', ''))
    return JSONResponse(folder)


@login_required
@permission_required('core.user_holder')
def json_image_view(request):
    user = get_gallery_user(request)
    if not user:
        raise Http404()
    if request.method == 'POST':
        try:
            path = request.POST.get('path')
            gallery_id = request.POST.get('gallery')
            images = request.POST.getlist('images[]')

            controller = ImageController(gallery_id, user)
            controller.setPath(path)
            controller.setChecked(images)
            return JSONResponse(dict(status='ok'))
        except Exception as e:
            return JSONResponse(dict(error=str(e)), status=400)

    return JSONResponse(dict(error='Need post request'), status=400)


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
        except IOError as e:
            raise Http404(e)

    raise Http404('No Image')