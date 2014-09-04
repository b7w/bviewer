# -*- coding: utf-8 -*-
import os
import sys
from setuptools import setup

if os.path.exists('bviewer/settings/local.py'):
    sys.stderr.write('Warn: remove "bviewer.settings.local"\n')
    os.unlink('bviewer/settings/local.py')

setup(
    name='bviewer',
    version='v1.1.2 dev',
    install_requires=[
        'django>=1.7,<1.8',
        'django-rq',
        'djangorestframework>=2.3,<2.4',
        'django-filter',
        'django-redis',
        'redis',
        'pytz',
        'ExifRead==2.0',
        # to build
        'pillow',
        'psycopg2',
    ],
    dependency_links=[
        "git+https://github.com/ianare/exif-py.git@develop#egg=ExifRead-2.0"
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
