# -*- coding: utf-8 -*-
import logging

from django.http import Http404
from django.shortcuts import render, redirect
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie

from bviewer.core import settings
from bviewer.core.controllers import GalleryController, ImageController, VideoController, get_gallery_user
from bviewer.core.utils import ResizeOptionsError, decor_on


logger = logging.getLogger(__name__)


@cache_page(60 * 60)
@vary_on_cookie
def ShowHome(request):
    """
    Show home pages with galleries
    """
    holder = get_gallery_user(request)
    if not holder:
        return ShowMessage(request, message='No user defined')

    controller = GalleryController(holder, request.user, holder.top_gallery_id)
    main = controller.get_object()
    if not main:
        return ShowMessage(request, message='No main gallery')
    galleries = controller.get_galleries()

    return render(request, 'core/galleries.html', {
        'main': main,
        'galleries': galleries,
    })


@cache_page(60 * 60)
@vary_on_cookie
def ShowGallery(request, id):
    """
    Show sub galleries or images with videos
    """
    holder = get_gallery_user(request)
    if not holder:
        return ShowMessage(request, message='No user defined')

    controller = GalleryController(holder, request.user, id)
    main = controller.get_object()
    if not main:
        return ShowMessage(request, message='No such gallery')
    galleries = controller.get_galleries()

    template = 'core/gallery.html' if controller.is_album() else 'core/galleries.html'
    videos = controller.get_videos()
    images = controller.get_images()

    return render(request, template, {
        'main': main,
        'galleries': galleries,
        'videos': videos,
        'images': images,
        'back': True,
    })


@cache_page(60 * 60 * 24)
@vary_on_cookie
def ShowImage(request, id):
    """
    Show image with description
    """
    holder = get_gallery_user(request)
    if not holder:
        return ShowMessage(request, message='No user defined')

    controller = ImageController(holder, request.user, id)
    image = controller.get_object()
    if image is None:
        return ShowMessage(request, message='No such image')

    return render(request, 'core/image.html', {
        'gallery': image.gallery,
        'image': image,
        'back': True,
    })


@cache_page(60 * 60 * 24)
@vary_on_cookie
def ShowVideo(request, id):
    """
    Show video with description
    """
    holder = get_gallery_user(request)
    if not holder:
        return ShowMessage(request, message='No user defined')

    controller = VideoController(holder, request.user, id)
    video = controller.get_object()
    if video is None:
        return ShowMessage(request, message='No such video')

    return render(request, 'core/video.html', {
        'gallery': video.gallery,
        'video': video,
        'back': True,
    })


@decor_on(settings.VIEWER_SERVE['CACHE'], cache_page, 60 * 60)
@vary_on_cookie
def DownloadVideoThumbnail(request, id):
    """
    Get video thumbnail from video hosting and cache it
    """
    holder = get_gallery_user(request)
    if not holder:
        raise Http404('No user defined')

    controller = VideoController(holder, request.user, id)
    video = controller.get_object()
    if video is None:
        raise Http404('No such video')

    try:
        return controller.get_response('small')
    except ResizeOptionsError as e:
        logger.error('id:%s, holder:%s \n %s', id, holder, e)
        return ShowMessage(request, message=e)
    except IOError as e:
        logger.error('id:%s, holder:%s \n %s', id, holder, e)
        raise Http404('Oops no video thumbnail found')


@decor_on(settings.VIEWER_SERVE['CACHE'], cache_page, 60 * 60 * 24)
@vary_on_cookie
def DownloadImage(request, size, id):
    """
    Get image with special size
    """
    holder = get_gallery_user(request)
    if not holder:
        raise Http404('No user defined')

    controller = ImageController(holder, request.user, id)
    image = controller.get_object()
    if image is None:
        raise Http404('No such image')

    try:
        return controller.get_response(size)
    except ResizeOptionsError as e:
        logger.error('id:%s, holder:%s \n %s', id, holder, e)
        return ShowMessage(request, message=e)
    except IOError as e:
        logger.error('id:%s, holder:%s \n %s', id, holder, e)
        return redirect('/static/core/img/gallery.png')


def ShowMessage(request, title='Error', info=None, message=None):
    """
    Show simple message with default title='Error', info=None, message=None
    """
    logger.warning('title:%s, info:%s \n %s', title, info, message)
    return render(request, 'core/message.html', {
        'title': title,
        'info': info,
        'message': message,
    })


def ShowAbout(request):
    """
    Show about page
    """
    holder = get_gallery_user(request)
    if not holder:
        return ShowMessage(request, message='No user defined')

    return render(request, 'core/about.html', {
        'title': holder.about_title,
        'text': holder.about_text,
    })