======================
Application management
======================

.. index:: Management


Adding content
==============

.. index:: Adding content, Content

| To add content login, and click profile link on a right side.
  On django admin site add new gallery (Home › Galleries). After creating follow  *edit* link in *Images* field.
  In new window find in file system your directory with images and check them. Save.

| To select gallery thumbnail, go to the gallery settings (Home › Galleries > Some gallery).
  At the bottom select one from appeared image. Save.

| To add video, go to videos (Home › Videos). Add video, in *Gallery* field select required gallery.


Application cache
=================

.. index:: Application cache
.. _application-cache:

| To clear images and zip archives cache run first command.
  Old files will be deleted if hole size will be bigger than :ref:`user available <proxy-user-model>`.
  To remove users cache directories run second.
  To remove main cache directory run third.

.. code-block:: python

    python manage.py clearcache
    python manage.py clearcache full
    fab clear

| It is better to run first command every hour.
  Open crontab file and add line to the end.

.. code-block:: bash

    sudo vim /etc/crontab
    00 *  * * *     believe   python  /home/believe/viewer/manage.py clearcache