# -*- coding: utf-8 -*-
#
# Sample for 'local.py' settings
#

from bviewer.settings.project import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

# https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '{{ db.name }}',
        'USER': '{{ db.user }}',
        'PASSWORD': '{{ db.password }}',
        'HOST': '{{ db.host }}',
        'PORT': '{{ db.port }}',
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
        'error': {
            'level': 'DEBUG',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': "{{ app.log_path }}/error.app.log",
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
    },
}

FORCE_SCRIPT_NAME = ''

VIEWER_CACHE_PATH = '{{ app.cache_path }}'
VIEWER_STORAGE_PATH = '{{ share.path }}'


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
ALLOWED_HOSTS = '{{ app.domains }}'.split()


EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = 25
EMAIL_HOST_USER = '{{ email.user }}'
EMAIL_HOST_PASSWORD = '{{ email.user }}'
EMAIL_USE_TLS = True

EXTRA_HTML = ""