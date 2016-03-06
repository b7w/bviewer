# -*- coding: utf-8 -*-
import os
import sys

from setuptools import setup

if os.path.exists('bviewer/settings/local.py'):
    sys.stderr.write('Warn: remove "bviewer.settings.local"\n')
    # os.unlink('bviewer/settings/local.py')

setup(
    name='bviewer',
    version='v1.1.3',
    install_requires=[
        'django==1.9.4',
        'django-rq==0.9.0',
        'djangorestframework==3.3.2',
        'django-filter==0.12.0',
        'django-redis==4.3.0',
        'redis==2.10.5',
        'rq==0.5.6',
        'pytz',
        'exifread==2.1.2',
        # to build
        'pillow==3.1.1',
        'psycopg2==2.6',
    ],
    packages=['bviewer', 'bviewer.api', 'bviewer.archive', 'bviewer.core', 'bviewer.profile', 'bviewer.settings',
              'bviewer.slideshow', 'bviewer.api.tests', 'bviewer.core.files', 'bviewer.core.management',
              'bviewer.core.migrations', 'bviewer.core.tests', 'bviewer.core.management.commands',
              'bviewer.slideshow.migrations'],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'bviewer = bviewer.runner:main',
        ],
    },
    url='https://bitbucket.org/b7w/bviewer',
    license='MIT',
    author='B7W',
    author_email='b7w@isudo.ru',
    description=open('readme.md').read(),
)
