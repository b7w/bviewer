# -*- coding: utf-8 -*-
import logging
from django.conf import settings
from django.contrib.auth.views import login, logout
from django.http import Http404
from django.shortcuts import render, redirect
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie

from bviewer.core.controllers import AlbumController, ImageController, VideoController, get_gallery
from bviewer.core.dao import user_dao
from bviewer.core.exceptions import ResizeOptionsError, FileError
from bviewer.core.forms import RegistrationForm
from bviewer.core.utils import decor_on, get_year_parameter


logger = logging.getLogger(__name__)

GALLERY_NOT_FOUND = 'No gallery found'


@cache_page(60 * 2)
@vary_on_cookie
def index_view(request):
    """
    Show home pages with albums
    """
    gallery = get_gallery(request)
    if not gallery:
        return message_view(request, message=GALLERY_NOT_FOUND)

    controller = AlbumController(gallery, request.user, uid=gallery.top_album_id)
    if not controller.exists():
        return message_view(request, message='No main album found')

    year_filter = get_year_parameter(request)

    main = controller.get_object()
    albums = controller.get_albums(year=year_filter)
    years = controller.get_available_years()

    return render(request, 'core/gallery.html', {
        'gallery': gallery,
        'main': main,
        'albums': albums,
        'year_filter': year_filter,
        'years': years,
    })


@cache_page(60 * 2)
@vary_on_cookie
def album_view(request, uid):
    """
    Show sub albums or images with videos
    """
    gallery = get_gallery(request)
    if not gallery:
        return message_view(request, message=GALLERY_NOT_FOUND)

    controller = AlbumController(gallery, request.user, uid=uid)
    if not controller.exists():
        return message_view(request, message='No such album')

    main = controller.get_object()
    albums, images, videos, years = None, None, None, None
    year_filter = get_year_parameter(request)
    if controller.is_album():
        template = 'core/album.html'
        videos = controller.get_videos()
        images = controller.get_images()
    else:
        template = 'core/gallery.html'
        albums = controller.get_albums()
        years = controller.get_available_years()

    return render(request, template, {
        'gallery': gallery,
        'main': main,
        'albums': albums,
        'videos': videos,
        'images': images,
        'year_filter': year_filter,
        'years': years,
        'back': dict(album_id=main.parent_id, home=gallery.top_album_id == main.parent_id),
    })


@cache_page(60 * 8)
@vary_on_cookie
def image_view(request, uid):
    """
    Show image with description
    """
    gallery = get_gallery(request)
    if not gallery:
        return message_view(request, message=GALLERY_NOT_FOUND)

    controller = ImageController(gallery, request.user, uid)
    if not controller.exists():
        return message_view(request, message='No such image')
    image = controller.get_object()

    return render(request, 'core/image.html', {
        'gallery': gallery,
        'album': image.album,
        'image': image,
        'back': dict(album_id=image.album_id),
    })


@cache_page(60 * 8)
@vary_on_cookie
def video_view(request, uid):
    """
    Show video with description
    """
    gallery = get_gallery(request)
    if not gallery:
        return message_view(request, message=GALLERY_NOT_FOUND)

    controller = VideoController(gallery, request.user, uid)
    if not controller.exists():
        return message_view(request, message='No such video')
    video = controller.get_object()

    return render(request, 'core/video.html', {
        'gallery': gallery,
        'album': video.album,
        'video': video,
        'back': dict(album_id=video.album_id),
    })


@decor_on(settings.VIEWER_DOWNLOAD_RESPONSE['CACHE'], cache_page, 60 * 8)
@vary_on_cookie
def download_video_thumbnail_view(request, uid):
    """
    Get video thumbnail from video hosting and cache it
    """
    gallery = get_gallery(request)
    if not gallery:
        raise Http404(GALLERY_NOT_FOUND)

    controller = VideoController(gallery, request.user, uid)
    if not controller.exists():
        raise Http404('No such video')

    try:
        return controller.get_response('small')
    except ResizeOptionsError as e:
        logger.error('id:%s, gallery:%s \n %s', uid, gallery, e)
        return message_view(request, message=e)
    except FileError as e:
        logger.error('id:%s, gallery:%s \n %s', uid, gallery, e)
        raise Http404('Oops no video thumbnail found')


@cache_page(60 * 8)
@vary_on_cookie
def video_redirect_view(request, uid):
    """
    Show video with description
    """
    gallery = get_gallery(request)
    if not gallery:
        return message_view(request, message=GALLERY_NOT_FOUND)

    controller = VideoController(gallery, request.user, uid)
    if not controller.exists():
        return message_view(request, message='No such video')
    video = controller.get_object()

    return redirect(controller.video_url(video))


@decor_on(settings.VIEWER_DOWNLOAD_RESPONSE['CACHE'], cache_page, 60 * 8)
@vary_on_cookie
def download_image_view(request, size, uid):
    """
    Get image with special size
    """
    gallery = get_gallery(request)
    if not gallery:
        raise Http404(GALLERY_NOT_FOUND)

    controller = ImageController(gallery, request.user, uid)
    if not controller.exists():
        raise Http404('No such image')

    try:
        return controller.get_response(size)
    except ResizeOptionsError as e:
        logger.error('id:%s, gallery:%s \n %s', uid, gallery, e)
        return message_view(request, message=e)
    except FileError as e:
        logger.error('id:%s, gallery:%s \n %s', uid, gallery, e)
        return redirect('/static/core/img/album.png')


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


@cache_page(60 * 8)
@vary_on_cookie
def about_view(request):
    """
    Show about page
    """
    gallery = get_gallery(request)
    if not gallery:
        return message_view(request, message=GALLERY_NOT_FOUND)

    return render(request, 'core/about.html', {
        'gallery': gallery,
        'title': gallery.about_title,
        'text': gallery.about_text,
    })


def login_view(request):
    """
    Proxy for `django.contrib.auth.views.login` + gallery check
    """
    gallery = get_gallery(request)
    if not gallery:
        return message_view(request, message=GALLERY_NOT_FOUND)
    return login(request, template_name='core/login.html', extra_context=dict(gallery=gallery))


def logout_view(request):
    """
    Proxy for `django.contrib.auth.views.logout` + gallery check
    """
    gallery = get_gallery(request)
    if not gallery:
        return message_view(request, message=GALLERY_NOT_FOUND)
    return logout(request, next_page='/')


def registration_view(request):
    """
    Register view
    """
    gallery = get_gallery(request)
    if not gallery:
        return message_view(request, message=GALLERY_NOT_FOUND)
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            user_dao.create_gallery_user(gallery, username, email, password)
            return redirect('/')

    else:
        form = RegistrationForm()
    return render(request, 'core/registration.html', {
        'form': form
    })