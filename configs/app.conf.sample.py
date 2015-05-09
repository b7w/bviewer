# -*- coding: utf-8 -*-
from bviewer.settings.project import *

DEBUG = False

SECRET_KEY = '2pn61g9w5$kvey611z2ua31szq(7)t0m0)$w#o)p@)ycj&93!!'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'bviewer',
        'USER': 'bviewer',
        'PASSWORD': 'root',
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
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    },
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

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


# Security
SESSION_COOKIE_SECURE = True

CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SECURE = True

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

X_FRAME_OPTIONS = 'DENY'

ALLOWED_HOSTS = '{{ domains }}'.split()


# Extra
FORCE_SCRIPT_NAME = ''


# Malling
SERVER_EMAIL = '{{ server_email }}'
DEFAULT_FROM_EMAIL = '{{ server_email }}'

EMAIL_HOST = 'smtp.bviewer.loc'
EMAIL_PORT = 25
EMAIL_HOST_USER = '{{ server_email }}'
EMAIL_HOST_PASSWORD = 'test'
EMAIL_USE_TLS = True


# Application
VIEWER_CACHE_PATH = '{{ cache_path }}'
VIEWER_STORAGE_PATH = '{{ share_path }}'

EXTRA_HTML = ''