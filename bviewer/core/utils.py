# -*- coding: utf-8 -*-
import re
import time
import logging
from hashlib import sha1

from django.core.cache import cache
from django.shortcuts import redirect
from django.utils.decorators import available_attrs
from django.utils.encoding import smart_text, smart_bytes
from django.utils.functional import wraps
from django_rq import get_queue

from bviewer.core import settings
from bviewer.core.models import ProxyUser


logger = logging.getLogger(__name__)


class RaisingRange:
    """
    Iterator range that double sum base value if item/base == 8

        >>> list(RaisingRange(32, start=0, base=1))
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 16, 20, 24, 28, 32]
    """

    def __init__(self, maximum, start=None, base=None):
        """
        Max value, start from or 0, base or 1

        :type maximum: int
        :type start: int
        :type base: int
        """
        self.value = start or 0
        self.base = base or 1
        self.max = maximum

    def __iter__(self):
        return self

    def next(self):
        if self.value <= self.max:
            tmp = self.value
            if self.value / self.base == 8:
                self.base *= 2
            self.value += self.base
            return tmp
        else:
            raise StopIteration

    def __str__(self):
        return str(list(self))


class ResizeOptionsError(Exception):
    """
    Resize options error.
    """
    pass


class ResizeOptions:
    """
    Options for resize such as width, height,
    max size - max of width/height,
    crop - need or not.
    """

    def __init__(self, size, user=None, storage=None, name=None):
        """
        Get sting with size "small" or "middle" or "big"
        user -> path to the user cache,
        storage -> path to the user storage,
        name -> file name.

        :type size: str
        :type user: str
        :type storage: str
        :type name: str
        """
        self.user = user
        self.storage = storage
        self.name = name
        self.width = 0
        self.height = 0
        self.size = 0
        self.crop = False
        self.quality = 95
        self.choose_setting(size)

    def choose_setting(self, size):
        """
        Select size by name from settings.VIEWER_IMAGE_SIZE.
        If not found - raise ResizeOptionsError.

        :type size: str
        """
        if size in settings.VIEWER_IMAGE_SIZE:
            self.from_settings(settings.VIEWER_IMAGE_SIZE[size])
        else:
            raise ResizeOptionsError('Undefined size format \'{0}\''.format(size))

    def from_settings(self, value):
        """
        Set values from settings.VIEWER_IMAGE_SIZE

        :type value: dict
        """
        self.width = value['WIDTH']
        self.height = value['HEIGHT']
        self.size = max(self.width, self.height)
        self.crop = 'CROP' in value and value['CROP'] is True
        if 'QUALITY' in value:
            self.quality = value['QUALITY']
            if not (80 <= self.quality <= 100):
                raise ResizeOptionsError('Image QUALITY settings have to be between 80 and 100')

    def __repr__(self):
        return smart_text('ResizeOptions({sz},user={us},storage={st},name={nm})') \
            .format(sz=self.size, us=self.user, st=self.storage, nm=self.name)


class FileUniqueName:
    """
    Create unique hash name for file

        >>> builder = FileUniqueName()
        >>> time = builder.time()
        >>> time
        1323242186.620497
        >>> builder.build("some/file", time=time)
        'fb41bb28d2614159246163f8dc77ac14'
        >>> builder.build("some/file", time=builder.time())
        '6ef61d7c41d391fcd17dd59e1d29dfc2'
        >>> builder.build("some/file", time=time, extra='tag1')
        'bb89a8697e7f2acfd5d904bc96ce5b81'
    """

    def __init__(self):
        pass

    def hash(self, name):
        """
        Return md5 of "files.storage" + name
        """
        return sha1('files.storage' + smart_bytes(name)).hexdigest()

    def time(self):
        """
        Return just time.time( )
        """
        return time.time()

    def build(self, path, time=None, extra=None):
        """
        return unique name of path + [extra]
        """
        full_name = settings.VIEWER_CACHE_PATH + path
        if time:
            if time is True:
                full_name += str(self.time())
            else:
                full_name += str(time)
        if extra:
            full_name += str(extra)
        return self.hash(full_name)


domain_match = re.compile(r'([w]{3})?\.?(?P<domain>[\w\.]+):?(\d{0,4})')


def get_gallery_user(request):
    """
    Get domain from request and try to find user with user.url == domain.
    If not try return authenticated user, else user from settings.VIEWER_USER_ID.

    :type request: django.http.HttpRequest
    :rtype: bviewer.core.models.ProxyUser
    """
    key = 'core.utils.get_gallery_user({0})'.format(request.get_host())
    data = cache.get(key)
    if data:
        return data
    if settings.VIEWER_USER_ID:
        user = ProxyUser.objects.get(id=settings.VIEWER_USER_ID)
        cache.set(key, user)
        return user

    match = domain_match.match(request.get_host())
    if match:
        url = match.group('domain')
        user = ProxyUser.objects.safe_get(url=url)
        if user:
            cache.set(key, user)
            return user

    if request.user.is_authenticated():
        return ProxyUser.objects.get(id=request.user.id)

    return None


def perm_any_required(*args, **kwargs):
    """
    Decorator for views that checks if at least one permission return True,
    redirecting to the `url` page on False.
    """
    url = kwargs.get('url', '/')

    def test_func(user):
        for perm in args:
            if user.has_perm(perm):
                return True

    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            return redirect(url)

        return _wrapped_view

    return decorator


def decor_on(conditions, decor, *args, **kwargs):
    """
    Return decorator with args and kwargs if conditions is True. Else function
    """

    def decorator(func):
        if conditions:
            return decor(*args, **kwargs)(func)
        return func

    return decorator


def cache_method(func):
    """
    Cache object methods, without any args!
    Set attr `'_' + func name`.
    """

    @wraps(func)
    def wrapped(self):
        name = '_' + func.__name__
        if hasattr(self, name):
            return getattr(self, name, None)
        cached = func(self)
        setattr(self, name, cached)
        return cached

    return wrapped


def as_job(func, queue='default', timeout=None, *args, **kwargs):
    rq = get_queue(name=queue)
    task = rq.enqueue(func, timeout=timeout, args=args, kwargs=kwargs)
    while not task.is_finished:
        time.sleep(0.1)
    return task.result