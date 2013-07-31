=============
Release notes
=============

.. index:: Release notes


| **v1.0.1**
| Add choice for asc/desc gallery sorting. Plus some clean up and improvements.
  Need database scheme update.

| ``ALTER TABLE core_gallery ADD COLUMN gallery_sorting smallint NOT NULL DEFAULT 1;``
  (v194:4b54f1ac9c78)

* Fix not playing video from js gallery
* Add RQ_DEBUG settings
* Move all settings to default django.settings package
* Edit documentation, add simple FAQ
* Make normal back link in galleries
* Improve logging and error handling
* Add timezone support


| **v1.0.0**
| First stable release. There can be some bugs and features.
  But all main ideas implemented and documentation ready.
  Look, feel, be happy :-)