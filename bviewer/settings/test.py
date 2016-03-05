# -*- coding: utf-8 -*-
#
# Default test settings
#
from bviewer.settings.local import *

TEST = True
RQ_DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'bviewer': {
            'handlers': ['null'],
        },
    }
}

RQ_QUEUES = {}

VIEWER_DOWNLOAD_RESPONSE = {
    'BACKEND': 'bviewer.core.files.response.django',
    'INTERNAL_URL': '/protected',
    'CACHE': False,
}

VIEWER_TESTS_PATH = os.path.join(PROJECT_PATH, 'tests')
VIEWER_STORAGE_PATH = os.path.join(VIEWER_TESTS_PATH, 'storage')
VIEWER_CACHE_PATH = os.path.join(VIEWER_TESTS_PATH, 'cache')
