# -*- coding: utf-8 -*-
import os
import sys
from setuptools import setup

if os.path.exists('bviewer/settings/local.py'):
    sys.stderr.write('Warn: remove "bviewer.settings.local"\n')
    #os.unlink('bviewer/settings/local.py')

setup(
    name='bviewer',
    version='v1.1.3 dev',
    install_requires=[
        'django==1.8.1',
        'django-rq==0.8.0',
        'djangorestframework==3.1.1',
        'django-filter==0.9.2',
        'django-redis==4.0.0',
        'redis==2.10.3',
        'pytz',
        'exifread==2.0.2',
        # to build
        'pillow==2.8.1',
        'psycopg2==2.6',
    ],
    packages=['bviewer', 'bviewer.api', 'bviewer.api.tests', 'bviewer.core', 'bviewer.core.files', 'bviewer.core.tests',
              'bviewer.core.management', 'bviewer.core.management.commands', 'bviewer.archive', 'bviewer.profile',
              'bviewer.settings', 'bviewer.slideshow', ],
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
