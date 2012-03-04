# -*- coding: utf-8 -*-

from django.utils.simplejson import JSONDecodeError

from core.models import Video, Gallery
from api.utils import JSONResponse, JSONRequest, login_required_ajax
from mongo.models import DocumentValidationError
from mongo.utils import perm_any_required

import logging

logger = logging.getLogger( __name__ )


@login_required_ajax
@perm_any_required( "user.holder", "api.video.get" )
def JsonVideoGet( request ):
    """
    Get video by `_id` or `gallery` and authenticated user
    """
    req = JSONRequest( request )
    if req.is_data( ):
        try:
            kwargs = req.data( )
            if "id" in kwargs:
                videos = Video.objects.safe_get( id=int( kwargs["id"] ), gallery__user=req.user.id )
            elif "gallery" in kwargs:
                videos = Video.objects.filter( gallery=int( kwargs["gallery"] ), gallery__user=req.user.id )
            else:
                return JSONResponse.Error( "Wrong query" )
            if not videos:
                return JSONResponse.Error( "No such images" )
            return JSONResponse( videos )
        except JSONDecodeError as e:
            return JSONResponse.Error( e )
        except DocumentValidationError as e:
            return JSONResponse.Error( e )
    else:
        return JSONResponse.Error( "Wrong request" )


@login_required_ajax
@perm_any_required( "user.holder", "api.video.update" )
def JsonVideoUpdate( request ):
    """
    Update video by `_id` and authenticated user
    """
    req = JSONRequest( request )
    if req.is_data( ):
        try:
            kwargs = req.data( )
            if "id" not in kwargs:
                return JSONResponse.Error( "Document must have '_id' key" )
            video = Video.objects.safe_get( id=int( kwargs["id"] ), gallery__user=req.user )
            if "uid" in kwargs:
                video.uid = kwargs["uid"]
            if "title" in kwargs:
                video.title = kwargs["title"]
            if "description" in kwargs:
                video.description = kwargs["description"]
            video.save( )
            return JSONResponse.Success( )
        except JSONDecodeError as e:
            return JSONResponse.Error( e )
        except DocumentValidationError as e:
            return JSONResponse.Error( e )
    else:
        return JSONResponse.Error( "Wrong request" )


@login_required_ajax
@perm_any_required( "user.holder", "api.video.add" )
def JsonVideoAdd( request ):
    """
    Add video, need video `uid` and `gallery` uid
    """
    req = JSONRequest( request )
    if req.is_data( ):
        try:
            kwargs = req.data( )
            if ("uid" and "gallery") not in kwargs:
                return JSONResponse.Error( "Document must have video 'uid' and 'gallery' uid keys" )
            gallery = Gallery.objects.safe_get( id=int( kwargs["gallery"] ), user=req.user )
            video = Video( gallery=gallery, uid=kwargs["uid"], title=kwargs["uid"] )
            video.save( )
            return JSONResponse.Success( )
        except JSONDecodeError as e:
            return JSONResponse.Error( e )
        except DocumentValidationError as e:
            return JSONResponse.Error( e )
    else:
        return JSONResponse.Error( "Wrong request" )


@login_required_ajax
@perm_any_required( "user.holder", "api.video.del" )
def JsonVideoRemove( request ):
    """
    Remove video by `_id` and authenticated user
    """
    req = JSONRequest( request )
    if req.is_data( ):
        try:
            kwargs = req.data( )
            if "id" not in kwargs:
                return JSONResponse.Error( "Document must have 'id' key" )
            id = int( kwargs["id"] )
            Video.objects.filter( id=id, gallery__user=req.user ).delete( )
            return JSONResponse.Success( )
        except JSONDecodeError as e:
            return JSONResponse.Error( e )
        except DocumentValidationError as e:
            return JSONResponse.Error( e )
    else:
        return JSONResponse.Error( "Wrong request" )