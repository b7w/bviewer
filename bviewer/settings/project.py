# -*- coding: utf-8 -*-
#
# Default project settings
#
from bviewer.settings.django import *

# If True - show debug toolbar
DEBUG_TOOL_BAR = DEBUG

# If True task run locally without RQ
RQ_DEBUG = DEBUG

# Hack to run test
TEST = False

# If album is used for one person or for tests
# set user id here
VIEWER_USER_ID = None


# Path where cache will be stored
# It is a resize images so it can be huge
# also it is soft links to full images
# check that this folder can be seen from nginx
# each user have his own sub folder
VIEWER_CACHE_PATH = NotImplemented


# Start path where full images are located
# each user can have his own home, in profile.storage
VIEWER_STORAGE_PATH = NotImplemented


# Sizes to resize images.
# Is it a map of maps. example - ``'small': {'WIDTH': 300, 'HEIGHT': 300, 'CROP': True}``
# By default crop is False, on True edges cut off.
# if image smaller than size it will be linked.
VIEWER_IMAGE_SIZE = {
    'tiny': {
        'WIDTH': 150,
        'HEIGHT': 150,
        'CROP': True,
        'QUALITY': 85,
    },
    'small': {
        'WIDTH': 300,
        'HEIGHT': 300,
        'CROP': True,
    },
    'big': {
        'WIDTH': 1920,
        'HEIGHT': 1080,
    },
    'full': {
        'WIDTH': 10 ** 6,
        'HEIGHT': 10 ** 6,
    },
}


# X-Accel-Redirect for web server to improve file serving, highly recommended!
# Set cache true to activate redirect response caching, it save 2 queries per image.
# Be careful, cache can't work with `django`! because it return hole file
VIEWER_DOWNLOAD_RESPONSE = {
    'BACKEND': 'bviewer.core.files.response.nginx',
    'INTERNAL_URL': '/protected',
    'CACHE': False,
}

# A string that fit before the closing body tag.
# For example some analytics HTML/JS code.
EXTRA_HTML = ''