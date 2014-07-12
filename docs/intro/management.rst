======================
Application management
======================

.. index:: Management


Application cache
=================

.. index:: Application cache
.. _application-cache:

| To clear images and zip archives cache run first command.
  Old files will be deleted if hole size will be bigger than :ref:`user available <proxy-user-model>`.
  To remove users cache directories run second.

.. code-block:: python

    python manage.py clearcache
    python manage.py clearcache full

| It is better to run first command every hour.
  Open crontab file and add line to the end.

.. code-block:: bash

    sudo vim /etc/crontab
    00 *  * * *     believe   python  /home/believe/viewer/manage.py clearcache