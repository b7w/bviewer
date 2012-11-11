# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.http import  HttpResponseRedirect


def redirect(url_name, *args, **kwargs):
    url = reverse(url_name, args=args)
    params = '&'.join('{0}={1}'.format(k, v) for k, v in kwargs.items() if v is not None)
    return HttpResponseRedirect(url + '?' + params)