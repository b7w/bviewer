===================
Quick install guide
===================

.. index:: Installation

| *There are a lot of ways to deploy it. This guide provide one simple way.*

Requirements
============

.. index:: Requirements

| Believe writen in python with `Django framework <https://www.djangoproject.com/>`__.
  Also it is need Redis database for cache and tasks.

| Application need these libraries to run:
  ``django``, ``django-rq``, ``django-tastypie``, ``redis``, ``fabric``, ``pillow or PIL``.
  And for development ``django-debug-toolbar``, ``mock``.
  For more details look ``requirements.txt``.

| You can use any django supported database server.
  It is officially works with PostgreSQL, MySQL, Oracle and SQLite.
  For more look `here <https://docs.djangoproject.com/en/dev/topics/install/#get-your-database-running>`__

.. note::

    App tested only with ubuntu 12.04, python 2.7, postgres 9.1 and nginx 1.2.


Database driver and image library
=================================

.. index:: Database driver, Image library

There is two ways. First install them from ubuntu package library.
Or install from source. The second is more preferred.

From packages
-------------

.. code-block:: bash

    sudo apt-get install python-pip python-psycopg2 python-imaging
    sudo pip install django-rq django-tastypie==0.9.15 django>=1.5 fabric pytz redis

From source
-----------

.. code-block:: bash

    sudo apt-get install python-dev python-pip
    sudo apt-get install libpq-dev
    sudo pip install psycopg2
    sudo apt-get install libjpeg-dev libfreetype6-dev zlib1g-dev
    sudo pip install -r requirements.txt


Redis database
==============

.. index:: Redis database

| For task queue bviewer use redis database. In default repositories version is too old.
  So it is needed to use ppa, *rwky/redis* for example.

.. code-block:: bash

    sudo apt-get install python-software-properties
    sudo add-apt-repository ppa:rwky/redis
    sudo apt-get update
    sudo apt-get install redis


Setup application
=================

.. index:: Setup application


| Copy sample setting file, and edit it.
  At least it is need to set :ref:`cache <CONF_VIEWER_CACHE_PATH>`, :ref:`storage path <CONF_VIEWER_STORAGE_PATH>`
  and :ref:`allowed hosts <CONF_ALLOWED_HOSTS>`.

.. code-block:: bash

    cp bviewer/settings/sample.py bviewer/settings/local.py
    vim bviewer/settings/local.py

| After run command to create tables in database. On syncing you will be prompt to create admin user.
  Then collect all static files from apps to one directory where web server can server it.

.. code-block:: bash

    python manage.py syncdb
    fab static


WSGI server
===========

.. index:: WSGI server, uwsgi

| To run application as daemon we install *uwsgi*.

.. code-block:: bash

    sudo apt-get install uwsgi uwsgi-plugin-python

| Than copy sample config and change paths in it according to yours installation folder.

.. code-block:: bash

    sudo cp docs/files/uwsgi.ini /etc/uwsgi/apps-available/uwsgi.ini
    sudo vim /etc/uwsgi/apps-available/uwsgi.ini
    sudo ln -s /etc/uwsgi/apps-available/uwsgi.ini /etc/uwsgi/apps-enabled/uwsgi.ini

| uwsgi.ini file content:

.. index:: uwsgi.ini

.. literalinclude:: /files/uwsgi.ini

| After restart usgi service.

.. code-block:: bash

    sudo service uwsgi restart

.. note::

    For background tasks, such as image processing by default starts 2 workers.
    With default and low queue.


Web server
==========

.. index:: Web server, nginx

| To run web server we need install *nginx*.

.. code-block:: bash

    sudo apt-get install nginx

| Than copy sample config. Change paths according to yours installation folder, change domains.

.. code-block:: bash

    sudo cp docs/files/nginx.conf /etc/nginx/apps-available/believe.conf
    sudo vim /etc/nginx/apps-available/believe.conf
    sudo ln -s /etc/nginx/apps-available/believe.conf /etc/nginx/apps-enabled/believe.conf

| nginx.conf file content:

.. index:: nginx.conf

.. literalinclude:: /files/nginx.conf

| After restart nginx service.

.. code-block:: bash

    sudo service nginx restart


What to read next
=================

| Read :doc:`Settings </ref/settings>`, :doc:`Management </intro/management>`.