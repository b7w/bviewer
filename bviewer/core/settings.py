# -*- coding: utf-8 -*-

from django.conf import settings

# Some setting that needed for tests
TESTS = False


# If gallery is used for one person or for tests
# set user id here
VIEWER_USER_ID = getattr(settings, 'VIEWER_USER_ID', None)


# Path where cache will bw stored
# It is a resize images so it can be huge
# also it is soft links to full images
# check that this folder can be seen from nginx
# each user have his own sub folder
VIEWER_CACHE_PATH = getattr(settings, 'VIEWER_CACHE_PATH', '../cache')


# Start path where full images are located
# each user will have his own home, in profile.storage
VIEWER_STORAGE_PATH = getattr(settings, 'VIEWER_STORAGE_PATH')


# Sizes to resize images.
# Is it a map of maps. example - `'small': {'WIDTH': 300, 'HEIGHT': 300, 'CROP': True}`
# By default crop is False, on True edges cut off.
# if image smaller than size it will be linked.
VIEWER_IMAGE_SIZE = getattr(settings, 'VIEWER_IMAGE_SIZE', {
    'small': {
        'WIDTH': 300,
        'HEIGHT': 300,
        'CROP': True,
    },
    'middle': {
        'WIDTH': 870,
        'HEIGHT': 600,
    },
    'big': {
        'WIDTH': 1280,
        'HEIGHT': 720,
    },
    'full': {
        'WIDTH': 10 ** 6,
        'HEIGHT': 10 ** 6,
    },
})


# X-Accel-Redirect for web server to improve file serving, highly recommended!
# Set cache true to activate redirect response caching, it save 2 queries per image.
# Be careful, it can't work with `default`! because it return hole file
VIEWER_SERVE = getattr(settings, 'VIEWER_SERVE', {
    'BACKEND': 'bviewer.core.files.serve.default',
    'INTERNAL_URL': '/protected',
    'CACHE': False,
})