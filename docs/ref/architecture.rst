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
  API - with `tastypie library <http://tastypieapi.org/>`__.


Project structure
=================

.. index:: Project structure

| Here brief lists of projects tree structure.
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
* **slideshow** - Module for slideshow that cat run on many galleries.
* **settings** - Django and project settings. Split and pack into python packages.
    * **django** - Default django settings setup for this project.
    * **project** - Settings used by application. Import django settings.
    * **local** - Local settings, like databases and folder paths. Import project -> django.
    * **test** - Settings to run unittests.  Import local -> project -> django.
    * **debug** - Settings to run debug server. Import local -> project -> django.
    * **sample** - Sample of local settings.
* **static** - Favicons and robots.txt.
* **templates** - Static templates for some error pages.


Holder profile
==============

.. index:: Holder profile

| Profile was made for gallery owners, where he can edit only his galleries and images.
  Technically it is sub class of django *AdminSite*.
  Plus some separate views to provide extra image managing.


SlideShow
=========

.. index:: SlideShow

| It is separate view. It can be call on group on galleries.
  Slideshow settings and status stored in relational database, image ids in Redis set.
  Slideshow attached to user via session_key.
  On slideshow creating each gallery put half random images to redis set.
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


Models
======

.. index:: Models

.. note::

    Models mentioned here very similar to the real, but not equal them!
    Some options can be omitted.

| Gallery, Image, Video models have special unique identifier. It is text field about 8-12 char length.
  It is made to provide way to hide some galleries. If all galleries with long complex urls,
  you can hide one form gallery tree and share it personally. Off course it is worth than authentication,
  but more simple to implement and use.

.. index:: ProxyUser model
.. _proxy-user-model:

| Special model for gallery holders with additional fields.
  **URL** - full domain name.
  **Home** - relative path from :ref:`VIEWER_STORAGE_PATH <CONF_VIEWER_STORAGE_PATH>`.
  **Cache size** - size in MB of user images cache, range [16, 256].
  **Cache archive size** - size in MB of user archives cache, range [128, 2048].
  **Top gallery** - witch gallery will be displayed on home page. The gallery is created automatically with user.
  **About title** - title for text in about page.
  **About text** - text in about page.

.. code-block:: python

    class ProxyUser(User):
        url = models.CharField(max_length=16, unique=True)
        home = models.CharField(max_length=256, blank=True, default='')
        cache_size = models.PositiveIntegerField(default=32)
        cache_archive_size = models.PositiveIntegerField(default=256)
        top_gallery = models.ForeignKey('Gallery', null=True)
        about_title = models.CharField(max_length=256)
        about_text = models.TextField(max_length=1024)

.. index:: Gallery model

| *Gallery model*
  **Parent** - for example ``ProxyUser.top_gallery`` to show on home page.
  **User** - not show on user profile, editable only by admin.
  **Visibility** - Type of visibility.
  VISIBLE - all user see in gallery tree and can access,
  HIDDEN - not visible in gallery tree but can be access if you know url,
  PRIVATE - visible and accessible only for gallery holder.
  *If parent is None it will be hidden from gallery tree for holder too.*
  **Gallery sorting** - Sort order of the nested galleries on time.
  ASK - Ascending, DESK - Descending.
  **allow_archiving** - Allow users to download images in archive
  **Thumbnail** - image of gallery tile.

.. code-block:: python

    class Gallery(models.Model):
        id = models.CharField(max_length=32, default=uuid_pk(length=8), primary_key=True)
        parent = models.ForeignKey('self', null=True)
        title = models.CharField(max_length=256)
        user = models.ForeignKey(ProxyUser)
        visibility = models.SmallIntegerField(max_length=1, choices=VISIBILITY_CHOICE, default=VISIBLE)
        gallery_sorting = models.SmallIntegerField(max_length=1, choices=SORT_CHOICE, default=ASK)
        allow_archiving = models.BooleanField(default=True)
        description = models.TextField(max_length=512, null=True)
        thumbnail = models.ForeignKey('Image', null=True)
        time = models.DateTimeField(default=datetime.now)

.. index:: Image model

| **Image model**. Store path to files. Do not store exif in database,
  images can be changed so this will to redundant file reads.
  **Gallery** - gallery FK.
  **Path** - relative path fom user home. For example: ``[/home/bviewer/data/[user]]/gallery1/img1.jpg``.
  **Time** - default time will be taken from image exif.

.. code-block:: python

    class Image(models.Model):
        id = models.CharField(max_length=32, default=uuid_pk(length=12), primary_key=True)
        gallery = models.ForeignKey(Gallery)
        path = models.CharField(max_length=256)
        time = models.DateTimeField(default=datetime.now)

.. index:: Video model

| **Video model**. Store Vimio or YouTube links.
  **UID** - vimio or YouTube video id.
  **Type** - VIMIO or YOUTUBE.
  **Gallery** - gallery FK.

.. code-block:: python

    class Video(models.Model):
        id = models.CharField(max_length=32, default=uuid_pk(length=12), primary_key=True)
        uid = models.CharField(max_length=32)
        type = models.SmallIntegerField(max_length=1, choices=TYPE_CHOICE, default=YOUTUBE)
        gallery = models.ForeignKey(Gallery)
        title = models.CharField(max_length=256)
        description = models.TextField(max_length=512, null=True)
        time = models.DateTimeField(default=datetime.now)

.. index:: Slideshow model

| **Slideshow model**. Store slideshow settings and status.
  **user** - Need to check permissions.
  **session_key** - To identify user.
  **timer** - Time between image switching.
  **status** - SlideShow status.
  NEW - Task added to queue.
  BUILD = Task done, slideshow can be viewed.
  FINISHED = All images shown.

.. code-block:: python

    class SlideShow(models.Model):
        id = models.CharField(max_length=32, default=uuid_pk(length=8), primary_key=True)
        gallery = models.ForeignKey(Gallery)
        user = models.ForeignKey(User, null=True)
        session_key = models.CharField(max_length=32)
        timer = models.SmallIntegerField(max_length=4, default=10)
        status = models.SmallIntegerField(max_length=1, choices=STATUS_CHOICE, default=NEW)
        image_count = models.IntegerField(max_length=8, default=0)
        time = models.DateTimeField(default=timezone.now)


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
