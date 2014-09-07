======================
Application management
======================

.. index:: Management


Application cache
=================

.. index:: Application cache
.. _application-cache:

| To clear images and zip archives cache run first command.
  Old files will be deleted if hole size will be bigger than :ref:`gallery available <gallery-model>`.
  To remove users cache directories run second.

.. code-block:: python

    python manage.py clearcache
    python manage.py clearcache full

| By default this command run every hour.


Check images
============

.. index:: Check images
.. _check-images:

| To detect images that not available on storage run `checkimages` command.
  It iterate all holders images and check that path exists.
  After send report to email if not found at least one.

.. code-block:: python

    python manage.py checkimages

| By default that command run at 00:00 every day.