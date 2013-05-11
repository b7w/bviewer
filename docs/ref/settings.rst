========
Settings
========

.. index:: Settings

| Sample settings can be found in ``bviewer/settings/sample.py``.
  There is not only viewer settings but
  `django framework too <https://docs.djangoproject.com/en/dev/ref/settings/>`__.


Viewer configuration
====================

VIEWER_USER_ID
---------------

.. _CONF_VIEWER_USER_ID:

Default: ``None``

| If gallery is used for one person or for tests set user id here.


VIEWER_CACHE_PATH
-----------------

.. _CONF_VIEWER_CACHE_PATH:

Required

| Path where cache will bw stored. It is a resize images so it can be huge.
  Also it is soft links to full images. Check that this folder can be seen from nginx.
  Each user have his own sub folder.


VIEWER_STORAGE_PATH
-------------------

.. _CONF_VIEWER_STORAGE_PATH:

Required

| Start path where full images are located.
  Each user can have his own home, in *profile.storage*.


VIEWER_IMAGE_SIZE
-----------------

.. _CONF_VIEWER_IMAGE_SIZE:

Default:

.. code-block:: python

    {
        'tiny': {
            'WIDTH': 150,
            'HEIGHT': 150,
            'CROP': True,
            'QUALITY': 85,
        },
        'small': {
            'WIDTH': 300,
            'HEIGHT': 300,
            'CROP': True,
        },
        'big': {
            'WIDTH': 1280,
            'HEIGHT': 720,
        },
        'full': {
            'WIDTH': 10 ** 6,
            'HEIGHT': 10 ** 6,
        },
    }

| Sizes to resize images. Is it a map of maps.
  Example - ``'small': {'WIDTH': 300, 'HEIGHT': 300, 'CROP': True, 'QUALITY': 95,}``.
  By default crop is False, on True edges cut off, quality equal 95%.
  If image smaller than size it will be linked.

| Tiny size used in admin to minimize cache size. Small size used in image thumbnails.
  Big size used for js gallery. Full size used to download real image.


VIEWER_DOWNLOAD_RESPONSE
------------------------

.. _CONF_VIEWER_DOWNLOAD_RESPONSE:

Default:

.. code-block:: python

    {
        'BACKEND': 'bviewer.core.files.response.django',
        'INTERNAL_URL': '/protected',
        'CACHE': False,
    }

| X-Accel-Redirect for web server to improve file serving, highly recommended!
  Set cache true to activate redirect response caching, it save 2 queries per image.
  Be careful, cache can't work with ``default``! because it return hole file.


Django configuration
====================

ALLOWED_HOSTS
-------------

.. _CONF_ALLOWED_HOSTS:

Default: ``[]``

| A list of domains for working app. For example ``dev.com``.
  It is a security measure. More details look
  `here <https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts>`__.