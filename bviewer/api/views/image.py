# -*- coding: utf-8 -*-

from bviewer.core.models import Image, Gallery
from bviewer.api.utils import JSONResponse, JSONRequest, login_required_ajax
from bviewer.core.utils import perm_any_required

import logging


logger = logging.getLogger( __name__ )


@login_required_ajax
@perm_any_required( "core.user_holder", "api.image.get" )
def JsonImagesGet( request ):
    """
    Get image by `_id` or `gallery` and authenticated user
    """
    req = JSONRequest( request )
    if req.is_data( ):
        try:
            kwargs = req.data( )
            images = None
            if "id" in kwargs:
                images = Image.objects.safe_get( id=int( kwargs["id"] ), user__id=req.user.id )
            elif "gallery" in kwargs:
                images = Image.objects.filter( gallery=int( kwargs["gallery"] ), gallery__user__id=req.user.id )
            else:
                return JSONResponse.Error( "Wrong query" )
            if not images:
                return JSONResponse.Error( "No such images" )
            return JSONResponse( images )
        except Exception as e:
            return JSONResponse.Error( e )
    else:
        return JSONResponse.Error( "Wrong request" )


@login_required_ajax
@perm_any_required( "core.user_holder", "api.image.add" )
def JsonImageAdd( request ):
    """
    Update image by `_id` or `gallery` and authenticated user
    """
    req = JSONRequest( request )
    if req.is_data( ):
        try:
            kwargs = req.data( )
            if ( "path" or "gallery" ) not in kwargs:
                return JSONResponse.Error( "Document must have 'gallery' and 'path' keys" )
            gallery = Gallery.objects.safe_get( id=kwargs["gallery"], user__id=req.user.id )
            if not gallery:
                return JSONResponse.Error( "No such gallery" )
            image = Image( gallery=gallery, path=kwargs["path"], )
            image.save( )

            return JSONResponse.Success( )
        except Exception as e:
            return JSONResponse.Error( e )
    else:
        return JSONResponse.Error( "Wrong request" )


@login_required_ajax
@perm_any_required( "core.user_holder", "api.image.del" )
def JsonImageRemove( request ):
    """
    Remove image by `_id` and authenticated user
    """
    req = JSONRequest( request )
    if req.is_data( ):
        try:
            kwargs = req.data( )
            if "id" not in kwargs:
                return JSONResponse.Error( "Document must have 'id' key" )
            id = int( kwargs["id"] )
            Image.objects.filter( id=id, gallery__user__id=req.user.id ).delete( )
            return JSONResponse.Success( )
        except Exception as e:
            return JSONResponse.Error( e )
    else:
        return JSONResponse.Error( "Wrong request" )