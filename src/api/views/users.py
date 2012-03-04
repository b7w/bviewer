# -*- coding: utf-8 -*-

from django.utils.simplejson import JSONDecodeError
from django.views.decorators.csrf import csrf_exempt

from api.utils import JSONResponse, JSONRequest, login_required_ajax
from core.models import ProxyUser, Image
from mongo.models import DocumentValidationError
from mongo.utils import perm_any_required

import logging

logger = logging.getLogger( __name__ )


@login_required_ajax
@perm_any_required( "user.holder", "api.gallery.get" )
def JsonUserGet( request ):
    """
    Get document of authenticated user
    """
    if request.method == 'GET':
        try:
            main = ProxyUser.objects.safe_get( id=request.user.id )
            if main is None:
                return JSONResponse.Error( "No such user" )

            return JSONResponse( main )
        except JSONDecodeError as e:
            return JSONResponse.Error( e )
    else:
        return JSONResponse.Error( "Wrong request" )


@csrf_exempt
@login_required_ajax
@perm_any_required( "user.holder", "api.user.update" )
def JsonUserUpdate( request ):
    """
    Update document of authenticated user.
    Fields 'avatar', 'about.title', 'about.text'
    """
    req = JSONRequest( request )
    if req.is_data( ):
        try:
            user = ProxyUser.objects.safe_get( id=request.user.id )
            kwargs = req.data( )
            if "avatar" in kwargs:
                user.avatar = Image.objects.safe_get( id=int( kwargs["avatar"] ), gallery__user=req.user )
            if "about.title" in kwargs:
                user.about_title = kwargs["about.title"]
            if "about.text" in kwargs:
                user.about_text = kwargs["about.text"]
            user.save( )
            return JSONResponse.Success( )
        except JSONDecodeError as e:
            return JSONResponse.Error( e )
        except DocumentValidationError as e:
            return JSONResponse.Error( e )
    else:
        return JSONResponse.Error( "Wrong request" )