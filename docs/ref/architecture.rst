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
  All functions and classes processing database models stored in *controls*.

* **api** - Simple REST tastypie api for basic models.
* **archive** - Some views and functions to create zip archive of one album.
* **core** - Main app, all base logic stored here.
    * **files** - Some logic to process files like storage access and serving.
    * **images** - Resizing and Caching of images, Exif data.
    * **settings** - main app setting, based on getattr from django settings.
* **profile** - Provide subclass of *AdminSite* for gallery owner with limited access.
* **settings** - Django settings but split and pack into python package.
* **static** - Favicons and robots.txt.
* **templates** - Static templates for 404 and 500 error pages.


Profile
=======

.. index:: Profile

| Profile was made for gallery owners, where he can edit only his galleries and images.
  Technically it is sub class of django *AdminSite*.
  Plus some separate views to provide ajax image managing.


Image storage
=============

.. index:: Image storage

| Application does not have any image/video upload system.
  Because from another hand complex file manager needed.
  For me - I'm already have image library mounted to the server, and I'm not want to copy past and store twice.

| So app need only some :ref:`folder <CONF_VIEWER_STORAGE_PATH>` where images stored.
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
  but is is more simple to implement and use.

.. index:: ProxyUser model

| Special model for gallery holders with additional fields.
  **url** - full domain name.
  **home** - relative path from :ref:`VIEWER_STORAGE_PATH <CONF_VIEWER_STORAGE_PATH>`.
  **cache_size** - size in MB of cache per user, than will ber cleared :ref:`periodically <application-cache>`.
  **top_gallery** - witch gallery will be displayed on home page. The gallery is created automatically with user.
  **about_title** - Title for text in about page.
  **about_text** - Text in about page.

.. code-block:: python

    class ProxyUser(User):
        url = models.CharField(max_length=16, unique=True)
        home = models.CharField(max_length=256, blank=True, default='')
        cache_size = models.PositiveIntegerField(default=32)
        top_gallery = models.ForeignKey('Gallery', null=True)
        about_title = models.CharField(max_length=256)
        about_text = models.TextField(max_length=1024)

.. index:: Gallery model

| Model to store tree galleries.
  **parent** - For example ``ProxyUser.top_gallery`` to show on home page.
  **user** - Not show on user profile, editable only by admin.
  **visibility** - type of visibility. VISIBLE - all user see in gallery tree and can access,
  HIDDEN - not visible in gallery tree but can be access if you new url,
  PRIVATE - visible and accessible only for gallery holder.
  **thumbnail** - Image of gallery tile.

.. code-block:: python

    class Gallery(models.Model):
        id = models.CharField(max_length=32, default=uuid_pk(length=8), primary_key=True)
        parent = models.ForeignKey('self', null=True)
        title = models.CharField(max_length=256)
        user = models.ForeignKey(ProxyUser)
        visibility = models.SmallIntegerField(max_length=1, choices=VISIBILITY_CHOICE, default=VISIBLE)
        description = models.TextField(max_length=512, null=True)
        thumbnail = models.ForeignKey('Image', null=True)
        time = models.DateTimeField(default=datetime.now)

.. index:: Image model

| Model to store path to images.
  **gallery** - Belonging to the gallery.
  **path** - relative path fom user home. For example: ``[/home/bviewer/data/[user]]/gallery1/img1.jpg``.
  **time** - if image add from profile gallery, time will be taken from exif.

.. code-block:: python

    class Image(models.Model):
        id = models.CharField(max_length=32, default=uuid_pk(length=12), primary_key=True)
        gallery = models.ForeignKey(Gallery)
        path = models.CharField(max_length=256)
        time = models.DateTimeField(default=datetime.now)

.. index:: Video model

| Model to store  Vimio or YouTube links.
  **uid** - Vimio or YouTube video id.
  **type** - VIMIO or YOUTUBE.
  **gallery** - Belonging to the gallery.

.. code-block:: python

    class Video(models.Model):
        id = models.CharField(max_length=32, default=uuid_pk(length=12), primary_key=True)
        uid = models.CharField(max_length=32)
        type = models.SmallIntegerField(max_length=1, choices=TYPE_CHOICE, default=YOUTUBE)
        gallery = models.ForeignKey(Gallery)
        title = models.CharField(max_length=256)
        description = models.TextField(max_length=512, null=True)
        time = models.DateTimeField(default=datetime.now)


Image processing
================

.. index:: Image processing

| All image resizing happens in separate processes via `Redis Queue <http://python-rq.org/>`__.
  The result stored in :ref:`cache <CONF_VIEWER_CACHE_PATH>`. If image is bigger link created.
  Cache name calculate from file last change time and resize options. Task added when first access happened.
  Image fully private and controlled by app, from outside there is no access to cache.
  To get image application send back special header, and nginx serve it manually.
  To read more go `wiki.nginx.org <http://wiki.nginx.org/X-accel>`__.

| For now there is one *feature*, while images resizing - django process hang.
