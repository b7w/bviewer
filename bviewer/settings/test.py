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

VIEWER_SERVE = {
    'BACKEND': 'bviewer.core.files.serve.default',
    'INTERNAL_URL': '/protected',
    'CACHE': False,
}