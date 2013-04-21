# -*- coding: utf-8 -*-

from bviewer.settings.local import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(TMP_PATH, "test.sqlite"),
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