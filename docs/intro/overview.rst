========
Overview
========

.. index:: Overview


About
=====

.. index:: About

| BelieveViewer is a simple photo gallery written in python with django.
  The main idea of this app is personal web photo sharing.
  There is no any comments, ratings, and other social stuff.
  There is no complex management system.

| Why this app was developed? I have not found any nice gallery with content management.
  All existing software was or too simple, or looks terrible.
  Public platforms change interface too often and do not provide privacy.

| BelieveViewer is open source project, released by MIT license.


Features
========

.. index:: Features

* | Gallery have nice dark template. It is scalable, and can be viewed on mobile devices.
    Images are cutting to square tile. For full image view there is js gallery that have navigation, slide show.

* | All images can be organized to albums. Each album can store another albums.
    Also you can specify simple description.

* | For privacy albums have some policies.
    Visible - visible for all users.
    Hidden - can be accessed via direct url, visible for users that have access rule for the gallery.
    Private - can be accessed only with users that have access rule for the gallery.

* | Images can't be upload to server via app, they have to stored there already.
    App automate resize and cache images. These parameters can be configured.

* | All real full size images in album can be download via zip archive.
    *Sub albums not included.*

* | Slideshow on album or random slideshow on group of albums.

* | Video can be add from Vimio or YouTube.

* | Simple about page for gallery description.

* | Application is multi user, each user need separate domain name.


Functional features
===================

.. index:: Functional features

| Here some specific programming items. Detail library dependencies can be viewed in *requirements.txt*.

* | Writen in python with Django framework.

* | All long operation run in separate RQ processes.

* | Need Redis DB for queue and cache.

* | Viewer serve images with help of nginx X-Accel-Redirect.


Screen shots
============

.. index:: Screen shots

**Home page, list of albums.**

.. image:: screen1.jpg
    :width: 100%


**Album with images**

.. image:: screen2.jpg
    :width: 100%


**JS album with full screen image**

.. image:: screen3.jpg
    :width: 100%