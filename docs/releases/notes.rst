=============
Release notes
=============

.. index:: Release notes

| **v1.0.3 dev**
| Some clean up

* Clear and rewrite a little css
* Remove link from preview to separate image view


| **v1.0.2** - *31.07.1013*
| Hot critical bug fix.

* Fix bug with wrong nginx response protected url


| **v1.0.1** - *31.07.1013*
| Add choice for asc/desc gallery sorting. Plus some clean up and improvements.
  Need database scheme update. Need update local.py setting file, change import statement.

| ``ALTER TABLE core_gallery ADD COLUMN gallery_sorting smallint NOT NULL DEFAULT 1;``

* Fix not playing video from js gallery
* Add RQ_DEBUG settings
* Move all settings to default django.settings package
* Edit documentation, add simple FAQ
* Make normal back link in galleries
* Improve logging and error handling
* Add timezone support


| **v1.0.0** - *13.07.1013*
| First stable release. There can be some bugs and features.
  But all main ideas implemented and documentation ready.
  Look, feel, be happy :-)