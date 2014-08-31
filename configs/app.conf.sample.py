# -*- coding: utf-8 -*-
from bviewer.settings.project import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

SECRET_KEY = '2pn61g9w5$kvey611z2ua31szq(7)t0m0)$w#o)p@)ycj&93!!'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'bviewer',
        'USER': 'bviewer',
        'PASSWORD': 'root',
        'HOST': '',
        'PORT': '',
        'TEST_NAME': 'bviewer_tmp',
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
        'error': {
            'level': 'DEBUG',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': "/home/bviewer/logs/bviewer.error.log",
            'mode': 'a',
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['mail_admins', 'error'],
            'level': 'ERROR',
            'propagate': True,
        },
        'bviewer': {
            'handlers': ['mail_admins', 'error'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.cache.RedisCache',
        'LOCATION': '127.0.0.1:6379:1',
    },
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'


FORCE_SCRIPT_NAME = ''

VIEWER_CACHE_PATH = '/home/bviewer/cache'
VIEWER_STORAGE_PATH = '/home/bviewer/share'


#
# RQ configs
#
RQ_QUEUES = {
    'default': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
    },
    'low': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
    },
}


#
# Run service configs
#
ALLOWED_HOSTS = '{{ domains }}'.split()

EMAIL_HOST = 'smtp.bviewer.loc'
EMAIL_PORT = 25
EMAIL_HOST_USER = 'noreply@bviewer.loc'
EMAIL_HOST_PASSWORD = 'test'
EMAIL_USE_TLS = True

EXTRA_HTML = ''