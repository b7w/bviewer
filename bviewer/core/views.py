# -*- coding: utf-8 -*-

import logging

from django.http import Http404
from django.shortcuts import render, redirect
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie

from bviewer.core import settings
from bviewer.core.utils import ResizeOptions, ResizeOptionsError, get_gallery_user, decor_on
from bviewer.core.files import Storage
from bviewer.core.files.serve import DownloadResponse
from bviewer.core.images import CacheImageAsync
from bviewer.core.models import Gallery, Image, Video


logger = logging.getLogger(__name__)


@cache_page(60 * 60)
@vary_on_cookie
def ShowHome(request, user=None):
    """
    Show home pages with galleries
    """
    holder, user_url = get_gallery_user(request, user)
    if not holder:
        return ShowMessage(request, message='No user defined')

    private = None if holder == request.user else False
    main, galleries = Gallery.get_galleries(holder.top_gallery_id, private)
    if not main:
        return ShowMessage(request, message='No main gallery')

    return render(request, 'core/galleries.html', {
        'path': request.path,
        'main': main,
        'galleries': galleries,
        'user_url': user_url,
    })


@cache_page(60 * 60)
@vary_on_cookie
def ShowGallery(request, id, user=None):
    """
    Show sub galleries or images with videos
    """
    id = int(id)
    holder, user_url = get_gallery_user(request, user)
    if not holder:
        return ShowMessage(request, message='No user defined')

    private = None if holder == request.user else False
    main, galleries = Gallery.get_galleries(id, private)
    if not main:
        return ShowMessage(request, message='No main gallery')

    videos = []
    images = []
    template = 'core/galleries.html'
    if not len(galleries):
        template = 'core/gallery.html'
        videos = Video.objects.filter(gallery__user__id=holder.id, gallery=id)
        images = Image.objects.filter(gallery__user__id=holder.id, gallery=id)

    return render(request, template, {
        'path': request.path,
        'main': main,
        'galleries': galleries,
        'videos': videos,
        'images': images,
        'user_url': user_url,
        'back': True,
    })


@cache_page(60 * 60 * 24)
@vary_on_cookie
def ShowImage(request, id, user=None):
    """
    Show image with description
    """
    holder, user_url = get_gallery_user(request, user)
    if not holder:
        return ShowMessage(request, message='No user defined')

    if holder == request.user:
        image = Image.objects.safe_get(gallery__user__id=holder.id, id=id)
    else:
        image = Image.objects.safe_get(gallery__user__id=holder.id, id=id, gallery__private=False)
    if image is None:
        return ShowMessage(request, message='No such image')

    return render(request, 'core/image.html', {
        'path': request.path,
        'gallery': image.gallery,
        'image': image,
        'user_url': user_url,
        'back': True,
    })


@cache_page(60 * 60 * 24)
@vary_on_cookie
def ShowVideo(request, id, user=None):
    """
    Show video with description
    """
    holder, user_url = get_gallery_user(request, user)
    if not holder:
        return ShowMessage(request, message='No user defined')

    if holder == request.user:
        video = Video.objects.safe_get(gallery__user__id=holder.id, id=id)
    else:
        video = Video.objects.safe_get(gallery__user__id=holder.id, id=id, gallery__private=False)
    if video is None:
        return ShowMessage(request, message='No such video')

    return render(request, 'core/video.html', {
        'path': request.path,
        'gallery': video.gallery,
        'video': video,
        'user_url': user_url,
        'back': True,
    })


@decor_on(settings.VIEWER_SERVE['CACHE'], cache_page, 60 * 60)
@vary_on_cookie
def DownloadVideoThumbnail(request, id, user=None):
    """
    Get video thumbnail from video hosting and cache it
    """
    holder, user_url = get_gallery_user(request, user)
    if not holder:
        raise Http404('No user defined')

    video = Video.objects.safe_get(gallery__user__id=holder.id, id=id)
    if video is None:
        raise Http404('No such video')
    name = video.uid + '.jpg'
    try:
        options = ResizeOptions('small', user=holder.url, storage=holder.home, name=str(video.id))
        image_async = CacheImageAsync(video.thumbnail_url, options)
        image_async.download()

        response = DownloadResponse.build(image_async.url, name)

    except ResizeOptionsError as e:
        logger.error('id:%s, holder:%s \n %s', id, holder, e)
        return ShowMessage(request, message=e)
    except IOError as e:
        logger.error('id:%s, holder:%s \n %s', id, holder, e)
        raise Http404('Oops no video thumbnail found')

    return response


@decor_on(settings.VIEWER_SERVE['CACHE'], cache_page, 60 * 60 * 24)
@vary_on_cookie
def DownloadImage(request, size, id, user=None):
    """
    Get image with special size
    """
    holder, user_url = get_gallery_user(request, user)
    if not holder:
        raise Http404('No user defined')

    if holder == request.user:
        image = Image.objects.safe_get(gallery__user__id=holder.id, id=id)
    else:
        image = Image.objects.safe_get(gallery__user__id=holder.id, id=id, gallery__private=False)
    if image is None:
        raise Http404('No such image')

    name = Storage.name(image.path)
    try:
        options = ResizeOptions(size, user=holder.url, storage=holder.home)
        image_async = CacheImageAsync(image.path, options)
        image_async.process()

        response = DownloadResponse.build(image_async.url, name)

    except ResizeOptionsError as e:
        logger.error('id:%s, holder:%s \n %s', id, holder, e)
        return ShowMessage(request, message=e)
    except IOError as e:
        logger.error('id:%s, holder:%s \n %s', id, holder, e)
        return redirect('/static/core/img/gallery.png')

    return response


def ShowMessage(request, title='Error', info=None, message=None):
    """
    Show simple message with default title='Error', info=None, message=None
    """
    logger.warning('title:%s, info:%s \n %s', title, info, message)
    return render(request, 'core/message.html', {
        'path': request.path,
        'title': title,
        'info': info,
        'message': message,
    })


def ShowAbout(request, user=None):
    """
    Show about page
    """
    holder, user_url = get_gallery_user(request, user)
    if not holder:
        return ShowMessage(request, message='No user defined')

    return render(request, 'core/about.html', {
        'path': request.path,
        'avatar': holder.avatar_id,
        'title': holder.about_title,
        'text': holder.about_text,
        'user_url': user_url,
    })