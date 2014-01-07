# -*- coding: utf-8 -*-
from django.conf import settings


def extra_html(request):
    """
    settings.EXTRA_HTML or None
    """
    return {
        'EXTRA_HTML': getattr(settings, 'EXTRA_HTML', ''),
    }
