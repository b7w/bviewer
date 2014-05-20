# -*- coding: utf-8 -*-
from bviewer.settings.local import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG
RQ_DEBUG = DEBUG

# By default templates in cache and dev server not see changes.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
INSTALLED_APPS += ('debug_toolbar',)

ALLOWED_HOSTS = ('*', )

VIEWER_DOWNLOAD_RESPONSE = {
    'BACKEND': 'bviewer.core.files.response.django',
    'INTERNAL_URL': '/protected',
    'CACHE': False,
}

#
# Debug toolbar configs
#

DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.profiling.ProfilingPanel',
)

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': 'bviewer.core.utils.show_toolbar',
}