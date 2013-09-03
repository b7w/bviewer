# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.contrib.auth.views import login, logout
from django.http import Http404
from django.shortcuts import render, redirect
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie

from bviewer.core.controllers import GalleryController, ImageController, VideoController, get_gallery_user
from bviewer.core.exceptions import ResizeOptionsError, FileError
from bviewer.core.utils import decor_on


logger = logging.getLogger(__name__)


@cache_page(60 * 60)
@vary_on_cookie
def index_view(request):
    """
    Show home pages with galleries
    """
    holder = get_gallery_user(request)
    if not holder:
        return message_view(request, message='No user defined')

    controller = GalleryController(holder, request.user, holder.top_gallery_id)
    main = controller.get_object()
    if not main:
        return message_view(request, message='No main gallery')
    galleries = controller.get_galleries()

    return render(request, 'core/galleries.html', {
        'holder': holder,
        'main': main,
        'galleries': galleries,
    })


@cache_page(60 * 60)
@vary_on_cookie
def gallery_view(request, uid):
    """
    Show sub galleries or images with videos
    """
    holder = get_gallery_user(request)
    if not holder:
        return message_view(request, message='No user defined')

    controller = GalleryController(holder, request.user, uid)
    main = controller.get_object()
    if not main:
        return message_view(request, message='No such gallery')
    galleries = controller.get_galleries()

    template = 'core/gallery.html' if controller.is_album() else 'core/galleries.html'
    videos = controller.get_videos()
    images = controller.get_images()

    return render(request, template, {
        'holder': holder,
        'main': main,
        'galleries': galleries,
        'videos': videos,
        'images': images,
        'back': dict(gallery_id=main.parent_id, home=holder.top_gallery_id == main.parent_id),
    })


@cache_page(60 * 60 * 24)
@vary_on_cookie
def image_view(request, uid):
    """
    Show image with description
    """
    holder = get_gallery_user(request)
    if not holder:
        return message_view(request, message='No user defined')

    controller = ImageController(holder, request.user, uid)
    image = controller.get_object()
    if image is None:
        return message_view(request, message='No such image')

    return render(request, 'core/image.html', {
        'holder': holder,
        'gallery': image.gallery,
        'image': image,
        'back': dict(gallery_id=image.gallery_id),
    })


@cache_page(60 * 60 * 24)
@vary_on_cookie
def video_view(request, uid):
    """
    Show video with description
    """
    holder = get_gallery_user(request)
    if not holder:
        return message_view(request, message='No user defined')

    controller = VideoController(holder, request.user, uid)
    video = controller.get_object()
    if video is None:
        return message_view(request, message='No such video')

    return render(request, 'core/video.html', {
        'holder': holder,
        'gallery': video.gallery,
        'video': video,
        'back': dict(gallery_id=video.gallery_id),
    })


@decor_on(settings.VIEWER_DOWNLOAD_RESPONSE['CACHE'], cache_page, 60 * 60)
@vary_on_cookie
def download_video_thumbnail_view(request, uid):
    """
    Get video thumbnail from video hosting and cache it
    """
    holder = get_gallery_user(request)
    if not holder:
        raise Http404('No user defined')

    controller = VideoController(holder, request.user, uid)
    video = controller.get_object()
    if video is None:
        raise Http404('No such video')

    try:
        return controller.get_response('small')
    except ResizeOptionsError as e:
        logger.error('id:%s, holder:%s \n %s', uid, holder, e)
        return message_view(request, message=e)
    except FileError as e:
        logger.error('id:%s, holder:%s \n %s', uid, holder, e)
        raise Http404('Oops no video thumbnail found')


@decor_on(settings.VIEWER_DOWNLOAD_RESPONSE['CACHE'], cache_page, 60 * 60)
@vary_on_cookie
def download_image_view(request, size, uid):
    """
    Get image with special size
    """
    holder = get_gallery_user(request)
    if not holder:
        raise Http404('No user defined')

    controller = ImageController(holder, request.user, uid)
    image = controller.get_object()
    if image is None:
        raise Http404('No such image')

    try:
        return controller.get_response(size)
    except ResizeOptionsError as e:
        logger.error('id:%s, holder:%s \n %s', uid, holder, e)
        return message_view(request, message=e)
    except FileError as e:
        logger.error('id:%s, holder:%s \n %s', uid, holder, e)
        return redirect('/static/core/img/gallery.png')


def message_view(request, title='Error', info=None, message=None):
    """
    Show simple message with default title='Error', info=None, message=None
    """
    logger.warning('title:%s, info:%s, %s', title, info, message)
    return render(request, 'core/message.html', {
        'title': title,
        'info': info,
        'message': message,
    })


def about_view(request):
    """
    Show about page
    """
    holder = get_gallery_user(request)
    if not holder:
        return message_view(request, message='No user defined')

    return render(request, 'core/about.html', {
        'holder': holder,
        'title': holder.about_title,
        'text': holder.about_text,
    })


def login_view(request):
    """
    Proxy for `django.contrib.auth.views.login` + holder check
    """
    holder = get_gallery_user(request)
    if not holder:
        return message_view(request, message='No user defined')
    return login(request, template_name='core/login.html', extra_context=dict(holder=holder))


def logout_view(request):
    """
    Proxy for `django.contrib.auth.views.logout` + holder check
    """
    holder = get_gallery_user(request)
    if not holder:
        return message_view(request, message='No user defined')
    return logout(request, next_page='/')