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
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
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
            'filename': "{{ log_path }}/bviewer.error.log",
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
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.file'

FORCE_SCRIPT_NAME = ''

VIEWER_CACHE_PATH = '{{ cache_path }}'
VIEWER_STORAGE_PATH = '{{ share_path }}'


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

SERVER_EMAIL = 'noreply@bviewer.loc'
DEFAULT_FROM_EMAIL = 'noreply@bviewer.loc'

EMAIL_HOST = 'smtp.bviewer.loc'
EMAIL_PORT = 25
EMAIL_HOST_USER = 'noreply@bviewer.loc'
EMAIL_HOST_PASSWORD = 'test'
EMAIL_USE_TLS = True

EXTRA_HTML = ''