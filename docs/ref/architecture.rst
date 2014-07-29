========================
Application architecture
========================

.. index:: Architecture


Framework
=========

.. index:: Framework

| To create this application `Django framework <https://www.djangoproject.com/>`__ was taken.
  It is very popular and have a lot of build in features or modules to cover app tasks.
  There is also experience of working with it.

| For example some modules that minimize work.
  User profile and image editing was build with help of standard django admin.
  API - with `django rest framework library <http://www.django-rest-framework.org/>`__.

Project structure
=================

.. index:: Project structure

| Here brief lists of project tree structure.
  Expected that you are familiar with django app structure.
  All small helper functions stored in *utils*.
  All functions and classes required for processing models are stored in *controls*.

* **api** - Simple REST tastypie api for basic models.
* **archive** - Some views and controls to create albums zip archives.
* **core** - Main app, all base logic stored here.
    * **files** - File system wrapper for storage access and image serving.
    * **exceptions** - All main exception classes.
    * **images** - Resizing and Image caching, Exif data.
* **profile** - Provide subclass of *AdminSite* for gallery owners with limited access.
* **slideshow** - Module for slideshow that cat run on multiple albums.
* **settings** - Django and project settings. Split and pack into python packages.
    * **django** - Default django settings setup for this project.
    * **project** - Settings used by application. Import django settings.
    * **local** - Local settings, like databases and folder paths. Import project -> django.
    * **test** - Settings to run unittests.  Import local -> project -> django.
    * **debug** - Settings to run debug server. Import local -> project -> django.
    * **sample** - Sample of local settings.
* **static** - Favicons and robots.txt.
* **templates** - Static templates for some error pages.


Models
======

.. index:: Models

.. note::

    Models mentioned here is not similar to the real!
    Many options are omitted.

| Album, Image, Video models have special unique identifier. It is text field about 8-12 char length.
  It is made to provide way to hide some albums. If all albums with long complex urls,
  you can hide one form album tree and share it personally. Off course it is worth than authentication,
  but more simple for using.


.. index:: Access model
.. _access-model:

| *Access model*. Add access to users for hidden and private albums. Also map users for galleries.

.. code-block:: python

    class Access(models.Model):
        user = models.ForeignKey(User)
        gallery = models.ForeignKey('Gallery')


.. index:: Gallery model
.. _gallery-model:

| *Gallery model*. Link user, domain, top album, plus sum configs.

.. code-block:: python

    class Gallery(models.Model):
        user = models.ForeignKey(User)
        # full domain name
        url = models.CharField(max_length=16, unique=True)
        # Relative path from :ref:`VIEWER_STORAGE_PATH <CONF_VIEWER_STORAGE_PATH>`.
        home = models.CharField(max_length=512)
        # Witch album will be displayed on home page. The album is created automatically with user.
        top_album = models.ForeignKey('Album')


.. index:: Album model
.. _album-model:

| *Album model*. Tree structure.

.. code-block:: python

    class Album(models.Model):
        id = models.CharField(max_length=32)
        parent = models.ForeignKey('self')
        gallery = models.ForeignKey(Gallery)
        visibility = models.SmallIntegerField(choices=VISIBILITY_CHOICE, default=VISIBLE)
        thumbnail = models.ForeignKey('Image')


.. index:: Image model
.. _image-model:

| *Image model*. Store paths to images.

.. code-block:: python

    class Image(models.Model):
        id = models.CharField(max_length=32)
        album = models.ForeignKey(Album)
        # Relative path fom user home
        # For example: [/home/bviewer/data/[user]]/album1/img1.jpg
        path = models.CharField(max_length=512)
        # Default time will be taken from image exif
        time = models.DateTimeField(default=timezone.now)


.. index:: Video model
.. _video-model:

| *Video model*. Store links to video providers.

.. code-block:: python

    class Video(models.Model):
        id = models.CharField(max_length=32)
        # Vimio or YouTube video id.
        uid = models.CharField(max_length=32)
        type = models.SmallIntegerField(choices=TYPE_CHOICE, default=YOUTUBE)
        album = models.ForeignKey(Album)


SlideShow
=========

.. index:: SlideShow

| It is separate view. It can be call on group on albums.
  Slideshow settings and status stored in relational database, image ids in Redis set.
  Slideshow attached to user via session_key.
  On slideshow creating each album put half random images to redis set.
  On next call from set selected and deleted random image.
  If no image in set, slideshow status is installed to Finish. And you need to create another one.


Image storage
=============

.. index:: Image storage

| Application does not have any image/video upload system.
  Because complex file manager needed. For me - I'm already have image library mounted to the server.
  And I'm not want to copy/past and store it twice.

| So app need only some :ref:`path <CONF_VIEWER_STORAGE_PATH>` where images stored.
  Each user can have *home* parameter that defines relative path of his root folder from main storage path.
  For example ``/home/bviewer/data/[user]``.
  Also it is better to give only *list* and *read* operation access for this directory and files.


Image processing
================

.. index:: Image processing

| All image resizing happens in separate processes via `Redis Queue <http://python-rq.org/>`__.
  The result stored in :ref:`cache <CONF_VIEWER_CACHE_PATH>`.
  On full image downloading or if :ref:`size <CONF_VIEWER_IMAGE_SIZE>` is bigger than real image, link created.
  Cache file name calculated from last change time and resize options. Task added when first access happened.
  Image fully private and controlled by app, from outside there is no access to cache.
  To get image, application send back special header, and nginx serve it manually.
  To read more go `wiki.nginx.org <http://wiki.nginx.org/X-accel>`__.

| For now there is one *feature*, while images resizing - django process hang.
