# -*- coding: utf-8 -*-

from datetime import datetime
from django.db import transaction
from core.images import ThreadCache

from core.models import Gallery, Image, Video
from api.utils import JSONResponse, JSONRequest, gallery_tree, login_required_ajax
from core.utils import get_gallery_user, perm_any_required, ResizeOptions

import logging

logger = logging.getLogger( __name__ )

@login_required_ajax
@perm_any_required( "core.user_holder", "api.gallery.get" )
def JsonGalleryGet( request ):
    """
    Get gallery by `_id` or `gallery` or `name` and authenticated user
    """
    req = JSONRequest( request )
    if req.is_data( ):
        try:
            kwargs = req.data( )
            main = None
            if "id" in kwargs:
                id = int( kwargs["id"] )
                main = Gallery.objects.safe_get( id=id, user__id=req.user.id )
            elif "title" in kwargs:
                main = Gallery.objects.safe_get( title=kwargs["title"], user__id=req.user.id )
            if main is None:
                return JSONResponse.Error( "No such gallery" )
            return JSONResponse( main )
        except Exception as e:
            return JSONResponse.Error( e )
    else:
        return JSONResponse.Error( "Wrong request" )


@login_required_ajax
@perm_any_required( "core.user_holder", "api.gallery.get" )
def JsonGalleryAll( request ):
    """
    Get list of all galleries names for authenticated user
    """
    if request.method == 'GET':
        try:
            main = Gallery.objects.filter( user__id=request.user.id )
            if not main:
                return JSONResponse.Error( "No such galleries" )
            all = [i.title for i in main]
            return JSONResponse( all )
        except Exception as e:
            return JSONResponse.Error( e )
    else:
        return JSONResponse.Error( "Wrong request" )


@login_required_ajax
@perm_any_required( "core.user_holder", "api.gallery.get" )
def JsonGalleryTree( request ):
    """
    Get gallery tree for authenticated user.
    It is a list with documents.
    Each document have '_id', 'id', 'name', 'children' list.
    """
    if request.method == 'GET':
        try:
            holder, user_url = get_gallery_user( request )
            main, galleries = Gallery.get_galleries( holder.top_gallery_id )
            if main is None:
                return JSONResponse.Error( "No main gallery" )

            tree = gallery_tree( holder.top_gallery_id )
            isolated = Gallery.objects.filter( parent=None ).exclude( id=holder.top_gallery_id )
            galleries = [tree]
            galleries.extend( [gallery_tree( i.id ) for i in isolated] )
            return JSONResponse( galleries )
        except Exception as e:
            return JSONResponse.Error( e )
    else:
        return JSONResponse.Error( "Wrong request" )


@login_required_ajax
@perm_any_required( "core.user_holder", "api.gallery.add" )
def JsonGalleryAdd( request ):
    """
    Add gallery for authenticated user
    """
    req = JSONRequest( request )
    if req.is_data( ):
        try:
            kwargs = req.data( )
            obj = Gallery( title=kwargs["title"], user_id=req.user.id )
            obj.save( )
            return JSONResponse( obj )
        except Exception as e:
            return JSONResponse.Error( e )
    else:
        return JSONResponse.Error( "Wrong request" )


@login_required_ajax
@perm_any_required( "core.user_holder", "api.gallery.update" )
def JsonGalleryUpdate( request ):
    """
    Update gallery by `_id` key for authenticated user
    """
    req = JSONRequest( request )
    if req.is_data( ):
        try:
            kwargs = req.data( )
            id = int( kwargs["id"] )
            main = Gallery.objects.safe_get( user__id=req.user.id, id=id )
            if main is None:
                return JSONResponse.Error( "No gallery" )
            if "title" in kwargs:
                main.title = kwargs["title"]
            if "time" in kwargs:
                main.time = datetime.strptime( kwargs["time"], "%d/%m/%Y" )
            if "thumbnail" in kwargs:
                image = Image.objects.safe_get( id=int( kwargs["thumbnail"] ), gallery__user__id=req.user.id )
                main.thumbnail = image
            if "description" in kwargs:
                main.description = kwargs["description"]
            main.save( )

            return JSONResponse.Success( )
        except Exception as e:
            return JSONResponse.Error( e )
    else:
        return JSONResponse.Error( "Wrong request" )


@login_required_ajax
@perm_any_required( "core.user_holder", "api.gallery.child" )
def JsonGalleryChild( request, action=None ):
    """
    Add or remove gallery child by `_id` key for authenticated user
    Need `child` key _id
    """
    req = JSONRequest( request )
    if req.is_data( ):
        try:
            kwargs = req.data( )
            if kwargs["id"] == kwargs["child"]:
                return JSONResponse.Error( "Id main and child is equal '{0}'".format( kwargs["id"] ) )
            id = int( kwargs["id"] )
            child_id = int( kwargs["child"] )
            main = Gallery.objects.safe_get( id=id, user=req.user )

            if main is None:
                return JSONResponse.Error( "No '{0}' gallery".format( id ) )

            child = Gallery.objects.safe_get( id=child_id, user__id=req.user.id )
            if child is None:
                return JSONResponse.Error( "No '{0}' gallery".format( child_id ) )

            if action == "add":
                child.parent = main
            elif action == "del":
                child.parent = None
            else:
                return JSONResponse.Error( "Wrong action '{0}'".format( action ) )
            child.save( )
            return JSONResponse.Success( )
        except Exception as e:
            return JSONResponse.Error( e )
    else:
        return JSONResponse.Error( "Wrong request" )


@login_required_ajax
@perm_any_required( "core.user_holder", "api.gallery.del" )
def JsonGalleryRemove( request ):
    """
    Remove gallery by `_id` key for authenticated user
    """
    req = JSONRequest( request )
    if req.is_data( ):
        try:
            kwargs = req.data( )
            id = int( kwargs["id"] )
            main = Gallery.objects.safe_get( id=id, user__id=req.user.id )
            if main is None:
                return JSONResponse.Error( "No such gallery" )
            with transaction.commit_on_success( ):
                Image.objects.filter( gallery=main ).delete( )
                Video.objects.filter( gallery=main ).delete( )
                main.delete( )
            return JSONResponse.Success( )
        except Exception as e:
            return JSONResponse.Error( e )
    else:
        return JSONResponse.Error( "Wrong request" )


@login_required_ajax
@perm_any_required( "core.user_holder", "api.gallery_precache" )
def JsonGalleryPreCache( request ):
    """
    Pre cache gallery in separate thread. Get id, each=1, size="small" | ["middle","big"]
    each=2 -> each second will be process and etc.
    """
    req = JSONRequest( request )
    if req.is_data( ):
        try:
            holder, user_url = get_gallery_user( request )
            kwargs = req.data( )
            if ( "id" and "size" ) not in kwargs:
                return JSONResponse.Error( "Wrong query. Required id, size str or list, each=1" )
            id = int( kwargs["id"] )
            each = 1
            if "each" in kwargs:
                each = int( kwargs["each"] )
            size = kwargs["size"]
            if isinstance( size, basestring ):
                if size == "full":
                    return JSONResponse.Error( "Size can not be full" )
                size = [size]
            elif "full" in size:
                return JSONResponse.Error( "Size can not be full" )

            images = Image.objects.filter( gallery=id, gallery__user__id=req.user.id )
            if not images:
                return JSONResponse.Error( "No such gallery" )

            paths = [images[i].path for i in range( 0, len( images ), each )]
            options = [ResizeOptions( s, user=holder.url, storage=holder.home ) for s in size]
            work = ThreadCache( paths, options )
            work.start( )

            return JSONResponse.Success( )
        except Exception as e:
            return JSONResponse.Error( e )
    else:
        return JSONResponse.Error( "Wrong request" )