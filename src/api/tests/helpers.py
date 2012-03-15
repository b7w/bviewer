# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.test.client import Client
from django.utils import simplejson

class ClientJson( Client ):
    def get_extra(self, path, data=None, follow=False, **extra):
        """
        Reverse url, if data add ?data={json dumps}
        """
        if data:
            params = simplejson.dumps( data, separators=(',', ':') )
            url = "{0}?data={1}".format( reverse( path ), params )
        else:
            url = reverse( path )
        result = super( ClientJson, self ).get( url, {}, follow, **extra )
        result.json = simplejson.loads( result.content )
        return result