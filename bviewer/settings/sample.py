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

VIEWER_CACHE_PATH = os.path.join(PROJECT_PATH, 'cache')
VIEWER_STORAGE_PATH = PROJECT_PATH

VIEWER_SERVE = {
    'BACKEND': 'bviewer.core.files.serve.nginx',
    'INTERNAL_URL': '/protected',
    'CACHE': True,
}

# When run clear old cache, for more examples look here
# http://ask.github.com/celery/userguide/periodic-tasks.html
VIEWER_CLEAR = {
    'minute': 0,
    'hour': 6,
}


#
# Celery configs
#
CELERY_IMPORTS = (
    'bviewer.core.tasks',
    'bviewer.archive.tasks',
)

# Use redis as a queue
BROKER_URL = "redis://localhost:6379/0"

# Store results in redis
CELERY_RESULT_BACKEND = "redis"
CELERY_REDIS_HOST = "localhost"
CELERY_REDIS_PORT = 6379
CELERY_REDIS_DB = 0


#
# Run service configs
#
PROCESS_USER = 'b7w'