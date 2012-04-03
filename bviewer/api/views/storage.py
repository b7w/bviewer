# -*- coding: utf-8 -*-

from bviewer.api.utils import JSONResponse, JSONRequest, login_required_ajax
from bviewer.core.files import Storage
from bviewer.core.utils import get_gallery_user, perm_any_required

import logging

logger = logging.getLogger( __name__ )


@login_required_ajax
@perm_any_required( "core.user_holder", "api.storage.list" )
def JsonStorageList( request ):
    """
    Get list of images in directory by `path` key.
    Return json like {"path": path, "back": back, "dirs": dirs, "files": files}.
    Where `path` is full path to current directory,
    `back` is full path to parent directory,
    `dirs` list of directory names,
    `files` list of file names.
    """
    req = JSONRequest( request )
    if req.is_data( ):
        try:
            kwargs = req.data( )
            holder, user_url = get_gallery_user( request )
            if not holder.home:
                return JSONResponse.Error( "You have no access to storage, check you profile" )
            storage = Storage( holder.home )
            if "path" not in kwargs:
                return JSONResponse.Error( "Request must have `path` key" )
            files = storage.list( kwargs["path"] )
            return JSONResponse( files )
        except Exception as e:
            return JSONResponse.Error( e )
    else:
        return JSONResponse.Error( "Wrong request" )