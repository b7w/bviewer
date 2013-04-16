# -*- coding: utf-8 -*-
import logging

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render

from bviewer.core.controllers import get_gallery_user
from bviewer.core.files import Storage
from bviewer.core.files.serve import DownloadResponse
from bviewer.core.images import CacheImage
from bviewer.core.utils import perm_any_required, ResizeOptions
from bviewer.profile.controllers import ImageController
from bviewer.profile.utils import JSONResponse


logger = logging.getLogger(__name__)


@login_required
@perm_any_required('core.user_holder')
def ShowImagesAdmin(request):
    user = get_gallery_user(request)
    if not user:
        raise Http404()
    return render(request, 'profile/images.html', {})


@login_required
@perm_any_required('core.user_holder')
def JsonStorageList(request):
    user = get_gallery_user(request)
    if not user:
        raise Http404()
    storage = Storage(user.home)
    folder = storage.list(request.GET.get('p', ''))
    return JSONResponse(folder)


@login_required
@perm_any_required('core.user_holder')
def JsonImageService(request):
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
@perm_any_required('core.user_holder')
def DownloadImage(request):
    if request.GET.get('p', None):
        path = request.GET['p']
        user = get_gallery_user(request)
        storage = Storage(user.home)
        try:
            if storage.exists(path):
                options = ResizeOptions('small', user=user.url, storage=user.home)
                image = CacheImage(path, options)
                image.process()
                name = Storage.name(path)
                response = DownloadResponse.build(image.url, name)
                return response
            raise Http404('No such file')
        except IOError as e:
            raise Http404(e)

    raise Http404('No Image')