======================
Application management
======================

.. index:: Management


Application cache
=================

.. index:: Application cache
.. _application-cache:

| To clear image and zip archive cache run first command.
  Files will be deleted if their size will be bigger than user available.
  First will be deleted bigger files, like archives.
  To remove all cache run second.

.. code-block:: python

    python manage.py clearcache
    fab clear

| It is better to run first command every day, for example on 5:00.
  Open crontab file and add line to the end.

.. code-block:: bash

    sudo vim /etc/crontab
    05 *  * * *     believe   python  /home/believe/viewer/manage.py clearcache


Adding content
==============

.. index:: Adding content, Content

| To add content login, and click profile link on a right side.
  On django admin site add new gallery (Home › Galleries). After creating follow  *edit* link in *Images* field.
  In new window find in file system your directory with images and check them. Save.

| To select gallery thumbnail, go to the gallery settings (Home › Galleries > Some gallery).
  At the bottom select one from appeared image. Save.

| To add video, go to videos (Home › Videos). Add video, in *Gallery* field select required gallery.