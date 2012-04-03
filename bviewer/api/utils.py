# -*- coding: utf-8 -*-

import datetime
from bson.objectid import ObjectId
from django.db.models.base import Model
from django.db.models.query import QuerySet

from django.http import HttpResponse
from django.utils import simplejson
from django.utils.decorators import available_attrs
from django.utils.functional import wraps

from bviewer.core.models import Gallery


class JSONEncoder( simplejson.JSONEncoder ):
    """
    Encode datetime to "%d/%m/%Y" and ObjectId
    """

    def default(self, obj):
        if isinstance( obj, (datetime.date, datetime.datetime) ):
            return obj.strftime( "%d/%m/%Y" )
        if isinstance( obj, ObjectId ):
            return str( obj )
        if issubclass( type( obj ), QuerySet ):
            return [i.for_json( ) for i in obj]
        if issubclass( type( obj ), Model ):
            return obj.for_json( )
        else:
            return simplejson.JSONEncoder.default( self, obj )


class JSONResponse( HttpResponse ):
    """
    Facade for HttpResponse that provide simple encode to json
    and some shortcuts for error and success message
    """

    def __init__(self, content, status=None, content_type=None):
        super( JSONResponse, self ).__init__( self.dumps( content ), "application/json", status, content_type )

    @classmethod
    def Error(cls, message):
        """
        Return {"error": message }
        """
        return JSONResponse( {"error": str( message )} )

    @classmethod
    def Success(cls):
        """
        Return {"success": True}
        """
        return JSONResponse( {"success": True} )

    def dumps(self, content):
        """
        Dumps to json with cls=JSONEncoder and indent=2
        """
        return simplejson.dumps( content, cls=JSONEncoder, indent=2 )


class JSONRequest:
    """
    Wrapper for request obj to check if there is some data in key 'data' of GET or POST request.
    Data must be in json format.
    """

    def __init__(self, request):
        self.request = request
        self.user = request.user
        self._data = None

    def is_auth(self):
        """
        Shortcut for is_authenticated
        """
        return self.user.is_authenticated( )

    def is_data(self):
        """
        return true if GET['data'] != None or POST['data'] != None.
        """
        if self.request.GET.get( "data", False ):
            self._data = self.request.GET["data"]
            return True
        elif self.request.POST.get( "data", False ):
            self._data = self.request.POST["data"]
            return True
        return False

    def data(self):
        """
        Return json load from GET['data'] or POST['data'], if first None.
        If nothing raise ValueError.
        """
        if self._data is None and not self.is_data( ):
            raise ValueError( "No data in request" )
        return simplejson.loads( self._data, encoding="UTF-8" )

    @classmethod
    def loadJson(cls, data):
        """
        Load json from string data in UTF-8 encoding
        """
        return simplejson.loads( data, encoding="UTF-8" )


def gallery_tree( root_id ):
    main = Gallery.objects.safe_get( id=root_id )
    query = Gallery.objects.filter( parent=root_id )
    if len( query ) != 0:
        nodes = [gallery_tree( i.id ) for i in query]
        return {"id": main.id, "title": main.title, "children": nodes}
    else:
        return {"id": main.id, "title": main.title}


def login_required_ajax( view_func, *args, **kwargs ):
    """
    This decorator do not redirect, it is return json error.
    """

    @wraps( view_func, assigned=available_attrs( view_func ) )
    def decorator(request, *args, **kwargs):
        if request.user.is_authenticated( ):
            return view_func( request, *args, **kwargs )
        return JSONResponse.Error( "You are not authenticated" )

    return decorator