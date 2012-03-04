# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render

from core.files.serve import DownloadResponse
from core.utils import Storage, ResizeOptions, CacheImage, get_gallery_user
from mongo.utils import perm_any_required

import logging

logger = logging.getLogger( __name__ )


@login_required
@perm_any_required( "user.holder" )
def ShowHome( request ):
    user, user_url = get_gallery_user( request, None )
    return render( request, "profile/home.html", {
        'path': request.path,
        'user_url': user_url,
        } )


@login_required
@perm_any_required( "user.holder" )
def ShowGalleries( request ):
    user, user_url = get_gallery_user( request, None )
    return render( request, "profile/galleries.html", {
        'path': request.path,
        'user_url': user_url,
        } )


@login_required
@perm_any_required( "user.holder" )
def ShowImages( request ):
    user, user_url = get_gallery_user( request, None )
    return render( request, "profile/images.html", {
        'path': request.path,
        'user_url': user_url,
        } )


@login_required
@perm_any_required( "user.holder" )
def ShowVideos( request ):
    user, user_url = get_gallery_user( request, None )
    return render( request, "profile/videos.html", {
        'path': request.path,
        'user_url': user_url,
        } )


@login_required
@perm_any_required( "user.holder" )
def ShowAbout( request ):
    user, user_url = get_gallery_user( request, None )
    return render( request, "profile/about.html", {
        'path': request.path,
        'user_url': user_url,
        } )


@login_required
@perm_any_required( "user.holder" )
def DownloadImage( request ):
    if request.GET.get( "p", None ):
        path = request.GET["p"]
        user, user_url = get_gallery_user( request, None )
        name = request.user.username
        if not user.home:
            return Http404( "You have no access to storage" )
        storage = Storage( user.home )
        try:
            if storage.exists( path ):
                options = ResizeOptions( "small", user=name, storage=user.home )
                image = CacheImage( path, options )
                image.process( )
                name = Storage.name( path )
                response = DownloadResponse.build( image.url, name )
                return response
            raise Http404( "No such file" )
        except IOError as e:
            raise Http404( e )

    raise Http404( "No Image" )