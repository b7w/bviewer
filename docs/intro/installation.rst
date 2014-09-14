===================
Quick install guide
===================

.. index:: Installation



Requirements
============

.. index:: Requirements

.. note::

    App tested only with Ubuntu 14.04, python 3.4 and PostgreSQL

| All main parts of installation are automated with fabric.
  For production use, database configuration required only.


Demo setup
==========

.. index:: Demo setup


| It is very easy to setup demo bviewer on virtual machine.
  All needed is application `source code <https://bitbucket.org/b7w/bviewer/downloads>`__,
   `virtual box <https://www.virtualbox.org>`__ and `vagrant <https://www.vagrantup.com>`__.

| Copy your sample images to `resources` folder. And run vagrant.

.. code-block:: bash

    vagrant up --provision

| Open https://4.4.4.4/ url and login.
  Demo account - `demo/root`. Admin account - `admin/root`.
  Enter profile page and create you first album.
  Admin console located on https://4.4.4.4/admin url.

.. note::

    Some ubuntu installations may required `linux-image-extra-virtual` package
    for unicode support in samba shares. Test with `modprobe nls_utf8`.


Installation
============

.. index:: Installation

| Almost all magic with server setup make fabric script.
  All you need to do is install PostgreSQL and correctly edit config files.

| First install PostgreSQL and create database with role that has create permissions.
  Open `configs` folder in the project.
  Create basic deploy configuration by renaming sample files and move it to dev folder.
  `conf.sample.txt` -> `dev/conf.txt`. (local config for `dev` env)

| **app.conf.py** - main application config. Enter valid database and email parameters.
  For detail configuration look :doc:`Settings </ref/settings>`.

| **nginx.ssl.crt** and **nginx.ssl.kry** - Nginx setup with both http and https access.
  Bu default samples crts used. You can override it in env config.

| **deploy.json** - fabric config. Here you can set application version (source revision),
  domains (nginx server names and django allowed hosts) and list of sambas shares.
  The last is simple wrapper for mount.cifs.

| Than run fabric. No meter if it first setup of update.
  The `dev` argument is `configs/dev` folder where we copy configs.
  You can keep any number of such folders for particular env.


.. code-block:: bash

    fab -H root@bviewer.loc --set env=dev deploy


What to read next
=================

| Read :doc:`Settings </ref/settings>`, :doc:`Management </intro/management>`.