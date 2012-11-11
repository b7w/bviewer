# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render

from bviewer.core.files import Storage
from bviewer.core.files.serve import DownloadResponse
from bviewer.core.images import CacheImage, BulkCache
from bviewer.core.models import Gallery, Image
from bviewer.core.utils import ResizeOptions, get_gallery_user, perm_any_required
from bviewer.profile.forms import GalleryForm
from bviewer.profile.utils import  redirect

import logging

logger = logging.getLogger(__name__)


@login_required
@perm_any_required("core.user_holder")
def ShowHome( request ):
    user, user_url = get_gallery_user(request)
    return render(request, "profile/home.html", {
        'tab_name': 'home',
        'path': request.path,
        'user_url': user_url,
    })


@login_required
@perm_any_required("core.user_holder")
def ShowGalleries( request ):
    user, user_url = get_gallery_user(request)
    if not user:
        raise Http404()
    galleries = Gallery.as_tree(user)

    id = request.GET.get('id') or user.top_gallery_id
    gallery = Gallery.objects.get(pk=id)
    if request.method == 'POST':
        form = GalleryForm(request.POST, instance=gallery)
        if form.is_valid():
            form.save()
    else:
        form = GalleryForm(instance=gallery)

    return render(request, "profile/galleries.html", {
        'tab_name': 'galleries',
        'path': request.path,
        'user_url': user_url,
        'galleries': galleries,
        'gallery': gallery,
        'form': form,
    })


@login_required
@perm_any_required("core.user_holder")
def GalleryAction( request, action ):
    user, user_url = get_gallery_user(request)
    if not user:
        raise Http404()

    id = int(request.GET.get('id') or 0)
    if action == 'add':
        name = request.GET.get('name')
        if name:
            obj = Gallery.objects.create(user=user, title=name)
            id = obj.id
    elif action == 'cache':
        step = request.GET.get('step') or 1
        size = request.GET.get('size') or 'small' # small|middle|big
        images = Image.objects.filter(gallery=id, gallery__user=user)
        if images:
            paths = [images[i].path for i in range(0, len(images), step)]
            work = BulkCache()
            work.appendTasks(paths, ResizeOptions(size, user=user.url, storage=user.home))
            work.send()
    elif action == 'set':
        parent_id = int(request.GET.get('parent'))
        if id != parent_id:
            new_upper = Gallery.objects.get(pk=parent_id)
            obj = Gallery.objects.get(pk=id)
            # check that we not make a loop
            # and set to child his parent
            if not new_upper.is_child_of(obj.id):
                obj.parent = new_upper
                obj.save()
    elif action == 'unset':
        Gallery.objects.filter(pk=id).update(parent=None)
    elif action == 'del':
        Gallery.objects.filter(pk=id).delete()
        id = None

    return redirect('profile.galleries', id=id)


@login_required
@perm_any_required("core.user_holder")
def ShowImages( request ):
    user, user_url = get_gallery_user(request)
    return render(request, "profile/images.html", {
        'tab_name': 'images',
        'path': request.path,
        'user_url': user_url,
    })


@login_required
@perm_any_required("core.user_holder")
def ShowVideos( request ):
    user, user_url = get_gallery_user(request)
    return render(request, "profile/videos.html", {
        'tab_name': 'videos',
        'path': request.path,
        'user_url': user_url,
    })


@login_required
@perm_any_required("core.user_holder")
def ShowAbout( request ):
    user, user_url = get_gallery_user(request)
    return render(request, "profile/about.html", {
        'tab_name': 'about',
        'path': request.path,
        'user_url': user_url,
    })


@login_required
@perm_any_required("core.user_holder")
def DownloadImage( request ):
    if request.GET.get("p", None):
        path = request.GET["p"]
        user, user_url = get_gallery_user(request)
        if not user.home:
            return Http404("You have no access to storage")
        storage = Storage(user.home)
        try:
            if storage.exists(path):
                options = ResizeOptions("small", user=user.url, storage=user.home)
                image = CacheImage(path, options)
                image.process()
                name = Storage.name(path)
                response = DownloadResponse.build(image.url, name)
                return response
            raise Http404("No such file")
        except IOError as e:
            raise Http404(e)

    raise Http404("No Image")