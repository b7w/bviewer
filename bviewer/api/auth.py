# -*- coding: utf-8 -*-

from django.conf import settings
from django.middleware.csrf import _sanitize_token
from django.utils.crypto import constant_time_compare
from django.utils.http import same_origin
from tastypie.authentication import Authentication
from tastypie.http import HttpUnauthorized


#TODO: this class copied from dev tastypie 0.9.12, remove it
class SessionAuthentication(Authentication):
    """
    An authentication mechanism that piggy-backs on Django sessions.

    This is useful when the API is talking to Javascript on the same site.
    Relies on the user being logged in through the standard Django login
    setup.

    Requires a valid CSRF token.
    """

    def is_authenticated(self, request, **kwargs):
        """
        Checks to make sure the user is logged in & has a Django session.
        """
        # Cargo-culted from Django 1.3/1.4's ``django/middleware/csrf.py``.
        # We can't just use what's there, since the return values will be
        # wrong.
        # We also can't risk accessing ``request.POST``, which will break with
        # the serialized bodies.
        if request.method in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            return request.user.is_authenticated()

        if getattr(request, '_dont_enforce_csrf_checks', False):
            return request.user.is_authenticated()

        csrf_token = _sanitize_token(request.COOKIES.get(settings.CSRF_COOKIE_NAME, ''))

        if request.is_secure():
            referer = request.META.get('HTTP_REFERER')

            if referer is None:
                return False

            good_referer = 'https://%s/' % request.get_host()

            if not same_origin(referer, good_referer):
                return False

        request_csrf_token = request.META.get('HTTP_X_CSRFTOKEN', '')

        if not constant_time_compare(request_csrf_token, csrf_token):
            return False

        return request.user.is_authenticated()

    def get_identifier(self, request):
        """
        Provides a unique string identifier for the requestor.

        This implementation returns the user's username.
        """
        return request.user.username


#TODO: this class copied from dev tastypie 0.9.12, remove it
class MultiAuthentication(object):
    """
    An authentication backend that tries a number of backends in order.
    """

    def __init__(self, *backends, **kwargs):
        super(MultiAuthentication, self).__init__(**kwargs)
        self.backends = backends

    def is_authenticated(self, request, **kwargs):
        """
        Identifies if the user is authenticated to continue or not.

        Should return either ``True`` if allowed, ``False`` if not or an
        ``HttpResponse`` if you need something custom.
        """
        unauthorized = False

        for backend in self.backends:
            check = backend.is_authenticated(request, **kwargs)

            if check:
                if isinstance(check, HttpUnauthorized):
                    unauthorized = unauthorized or check
                else:
                    request._authentication_backend = backend
                    return check

        return unauthorized

    def get_identifier(self, request):
        """
        Provides a unique string identifier for the requestor.

        This implementation returns a combination of IP address and hostname.
        """
        try:
            return request._authentication_backend.get_identifier(request)
        except AttributeError:
            return 'nouser'