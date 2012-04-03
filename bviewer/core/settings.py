# -*- coding: utf-8 -*-

from django.conf import settings

# Path where cache will bw stored
# It is a resize images so it can be huge
# also it is soft links to full images
# check that this folder can be seen from nginx
# each user have his own sub folder
VIEWER_CACHE_PATH = getattr( settings, 'VIEWER_CACHE_PATH', "../cache" )

# When run clear old cache, for more examples look here
# http://ask.github.com/celery/userguide/periodic-tasks.html
# default 6:00 hours
VIEWER_CLEAR = getattr( settings, 'VIEWER_CLEAR', {'minute': 0, 'hour': 6} )

# Start path where full images are located
# each user will have his own home, in profile.storage
VIEWER_STORAGE_PATH = getattr( settings, 'VIEWER_STORAGE_PATH' )

VIEWER_SMALL_SIZE = getattr( settings, 'VIEWER_SMALL_SIZE', {
    'WIDTH': 200,
    'HEIGHT': 200,
    'CROP': True,
    } )

VIEWER_MIDDLE_SIZE = getattr( settings, 'VIEWER_MIDDLE_SIZE', {
    'WIDTH': 870,
    'HEIGHT': 600,
    'CROP': False,
    } )

VIEWER_BIG_SIZE = getattr( settings, 'VIEWER_BIG_SIZE', {
    'WIDTH': 1280,
    'HEIGHT': 720,
    'CROP': False,
    } )

# X-Accel-Redirect for web server to improve file serving
VIEWER_SERVE = getattr( settings, 'VIEWER_SERVE', {
    'BACKEND': 'bviewer.core.files.serve.default',
    'INTERNAL_URL': '/protected',
    } )