# -*- coding: utf-8 -*-
import time
import logging

from django.conf import settings
from django.utils.encoding import smart_text, smart_bytes
from django.utils.functional import wraps
from django_rq import get_queue

from bviewer.core.exceptions import ResizeOptionsError


logger = logging.getLogger(__name__)


class RaisingRange(object):
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
        self.max = maximum
        self.start = start or 0
        self.base = base or 1
        self.value = self.start

    def __iter__(self):
        return self

    def next(self):
        if self.value <= self.max:
            tmp = self.value
            if (self.value - self.start) / self.base == 8:
                self.base *= 2
            self.value += self.base
            return tmp
        else:
            raise StopIteration

    def __str__(self):
        return str(list(self))


class ImageOptions(object):
    """
    Options for resize such as width, height,
    max size - max of width/height,
    crop - need or not.
    """

    def __init__(self, width=0, height=0, crop=False, quality=95, name=None):
        """
        :type name: str
        """
        self.width = width
        self.height = height
        self.size = max(self.width, self.height)
        self.crop = crop
        self.quality = quality
        self.name = smart_bytes(name) if name else None
        if not (80 <= quality <= 100):
            raise ResizeOptionsError('Image QUALITY settings have to be between 80 and 100')

    @classmethod
    def from_settings(cls, size_name, name=None):
        """
        Select size by name from settings.VIEWER_IMAGE_SIZE.
        If not found - raise ResizeOptionsError.

        :type size_name: str
        :rtype: ImageOptions
        """
        if size_name in settings.VIEWER_IMAGE_SIZE:
            value = settings.VIEWER_IMAGE_SIZE[size_name]
            return ImageOptions(
                width=value['WIDTH'],
                height=value['HEIGHT'],
                crop='CROP' in value and value['CROP'] is True,
                quality=value.get('QUALITY', 95),
                name=name,
            )
        else:
            raise ResizeOptionsError('Undefined size format \'{0}\''.format(size_name))

    def __repr__(self):
        return smart_text('ImageOptions(width={w}, height={h}, crop={c}, quality={q}, name={n})') \
            .format(w=self.width, h=self.height, c=self.crop, q=self.quality, n=self.name)


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


def as_job(func, queue='default', timeout=None, waite=True, args=None, kwargs=None):
    """
    Add `func(*args, **kwargs)` to RQ. And waite for result, if `waite`.
    """
    if settings.RQ_DEBUG:
        args = args or tuple()
        kwargs = kwargs or dict()
        return func(*args, **kwargs)
    rq = get_queue(name=queue)
    task = rq.enqueue(func, timeout=timeout, args=args, kwargs=kwargs)
    if waite:
        while not task.is_finished:
            time.sleep(0.1)
    return task.result


def method_call_str(func_name, self, *args, **kwargs):
    """
    Make code string

        >>> str(method_call_str('some', 'object', 1, 2, flag=True))
        'object.some(1, 2, flag=True)'
    """
    func_format = '{o}.{n}({a}, {kw})' if kwargs else '{o}.{n}({a})'
    str_args = smart_text(', ').join(map(smart_text, args))
    str_kwargs_pairs = [smart_text('{0}={1}').format(k, smart_text(v)) for k, v in kwargs.items()]
    str_kwargs = smart_text(', ').join(str_kwargs_pairs)
    return smart_text(func_format).format(o=self, n=func_name, a=str_args, kw=str_kwargs)