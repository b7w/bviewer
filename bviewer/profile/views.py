# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render

from bviewer.core.files import Storage
from bviewer.core.files.serve import DownloadResponse
from bviewer.core.images import CacheImage
from bviewer.core.utils import ResizeOptions, get_gallery_user, perm_any_required

import logging

logger = logging.getLogger( __name__ )


@login_required
@perm_any_required( "core.user_holder" )
def ShowHome( request ):
    user, user_url = get_gallery_user( request )
    return render( request, "profile/home.html", {
        'path': request.path,
        'user_url': user_url,
        } )


@login_required
@perm_any_required( "core.user_holder" )
def ShowGalleries( request ):
    user, user_url = get_gallery_user( request )
    return render( request, "profile/galleries.html", {
        'path': request.path,
        'user_url': user_url,
        } )


@login_required
@perm_any_required( "core.user_holder" )
def ShowImages( request ):
    user, user_url = get_gallery_user( request )
    return render( request, "profile/images.html", {
        'path': request.path,
        'user_url': user_url,
        } )


@login_required
@perm_any_required( "core.user_holder" )
def ShowVideos( request ):
    user, user_url = get_gallery_user( request )
    return render( request, "profile/videos.html", {
        'path': request.path,
        'user_url': user_url,
        } )


@login_required
@perm_any_required( "core.user_holder" )
def ShowAbout( request ):
    user, user_url = get_gallery_user( request )
    return render( request, "profile/about.html", {
        'path': request.path,
        'user_url': user_url,
        } )


@login_required
@perm_any_required( "core.user_holder" )
def DownloadImage( request ):
    if request.GET.get( "p", None ):
        path = request.GET["p"]
        user, user_url = get_gallery_user( request )
        if not user.home:
            return Http404( "You have no access to storage" )
        storage = Storage( user.home )
        try:
            if storage.exists( path ):
                options = ResizeOptions( "small", user=user.url, storage=user.home )
                image = CacheImage( path, options )
                image.process( )
                name = Storage.name( path )
                response = DownloadResponse.build( image.url, name )
                return response
            raise Http404( "No such file" )
        except IOError as e:
            raise Http404( e )

    raise Http404( "No Image" )