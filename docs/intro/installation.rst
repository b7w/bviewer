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

| Copy your sample images to `resources` folder. Enter `configs` folder.
  Create basic deploy configuration by renaming sample files.
  And run vagrant.

.. code-block:: bash

    vagrant up --provision

| Open https://4.4.4.4/ url, enter profile and create you first album.
  Demo account - `demo/root`. Admin account - `admin/root`.
  Admin console located on https://4.4.4.4/admin url.

.. note::

    Some ubuntu installations may required `linux-image-extra-virtual` package
    for unicode support in samba shares. Test `modprobe nls_utf8`.



What to read next
=================

| Read :doc:`Settings </ref/settings>`, :doc:`Management </intro/management>`.