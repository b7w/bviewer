# -*- coding: utf-8 -*-

from bviewer.settings.local import *

TEST = True

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

VIEWER_DOWNLOAD_RESPONSE = {
    'BACKEND': 'bviewer.core.files.response.django',
    'INTERNAL_URL': '/protected',
    'CACHE': False,
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'null': {
            'class': 'django.utils.log.NullHandler',
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

VIEWER_STORAGE_PATH = os.path.join(PROJECT_PATH, VIEWER_CACHE_PATH, 'storage')