# -*- coding: utf-8 -*-
#
# Sample for 'local.py' settings
#
import os

from bviewer.settings.django import *

# https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'Believe',
        'USER': 'Test',
        'PASSWORD': 'root',
        'HOST': 'localhost',
        'PORT': '',
        'TEST_NAME': 'Test',
    }
}

# https://docs.djangoproject.com/en/dev/topics/logging/#configuring-logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(levelname)-6s %(asctime)s - %(name)s - %(funcName)s %(lineno)d, %(message)s',
            'datefmt': '%Y %b %d, %H:%M:%S',
        },
    },
    'handlers': {
        'log-file': {
            'level': 'ERROR',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': os.path.join(PROJECT_PATH, "tmp/app.log"),
            'mode': 'a',
            'formatter': 'simple',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['log-file'],
            'level': 'ERROR',
            'propagate': True,
        },
        'bviewer': {
            'handlers': ['log-file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    },
}

FORCE_SCRIPT_NAME = ''

# app config
VIEWER_CACHE_PATH = os.path.join(PROJECT_PATH, 'cache')
VIEWER_STORAGE_PATH = PROJECT_PATH

VIEWER_SERVE = {
    'BACKEND': 'bviewer.core.files.serve.nginx',
    'INTERNAL_URL': '/protected',
    'CACHE': True,
}

# RQ configs
RQ_QUEUES = {
    'default': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
    },
}

# https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-ALLOWED_HOSTS
ALLOWED_HOSTS = ('.dev.loc', )