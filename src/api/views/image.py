# -*- coding: utf-8 -*-

from django.utils.simplejson import JSONDecodeError

from core.models import Image, Gallery
from api.utils import JSONResponse, JSONRequest, login_required_ajax
from mongo.models import DocumentValidationError
from mongo.utils import perm_any_required

import logging

logger = logging.getLogger( __name__ )


@login_required_ajax
@perm_any_required( "user.holder", "api.image.get" )
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
                images = Image.objects.safe_get( id=int( kwargs["id"] ), user=req.user )
            elif "gallery" in kwargs:
                images = Image.objects.filter( gallery=int( kwargs["gallery"] ), gallery__user=req.user )
            else:
                return JSONResponse.Error( "Wrong query" )
            if not images:
                return JSONResponse.Error( "No such images" )
            return JSONResponse( images )
        except JSONDecodeError as e:
            return JSONResponse.Error( e )
        except DocumentValidationError as e:
            return JSONResponse.Error( e )
    else:
        return JSONResponse.Error( "Wrong request" )


@login_required_ajax
@perm_any_required( "user.holder", "api.image.add" )
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
            gallery = Gallery.objects.safe_get( id=kwargs["gallery"], user=req.user )
            if not gallery:
                return JSONResponse.Error( "No such gallery" )
            image = Image( gallery=gallery, path=kwargs["path"], )
            image.save( )

            return JSONResponse.Success( )
        except JSONDecodeError as e:
            return JSONResponse.Error( e )
        except DocumentValidationError as e:
            return JSONResponse.Error( e )
    else:
        return JSONResponse.Error( "Wrong request" )


@login_required_ajax
@perm_any_required( "user.holder", "api.image.del" )
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
            Image.objects.filter( id=id, gallery__user=req.user ).delete( )
            return JSONResponse.Success( )
        except JSONDecodeError as e:
            return JSONResponse.Error( e )
        except DocumentValidationError as e:
            return JSONResponse.Error( e )
    else:
        return JSONResponse.Error( "Wrong request" )