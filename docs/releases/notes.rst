=============
Release notes
=============

.. index:: Release notes

| **v1.1 dev**
| Change database architecture. Need database scheme update.

| ``ALTER TABLE core_profile RENAME COLUMN top_gallery_id TO top_album_id;``
| ``ALTER TABLE core_gallery RENAME COLUMN gallery_sorting TO album_sorting;``
| ``ALTER TABLE core_image RENAME COLUMN gallery_id TO album_id;``
| ``ALTER TABLE core_video RENAME COLUMN gallery_id TO album_id;``
| ``ALTER TABLE core_gallery RENAME TO core_album;``
| ``ALTER TABLE slideshow_slideshow RENAME COLUMN gallery_id TO album_id;``

* Refactor all *gallery* to *album*


| **v1.0.9** - 4.06.2014
| Add some features to profile and improve mobile styles.

* Fix menu links on ipad
* Pre cache function
* On setting gallery allow archive set child too
* Image popup in profile list images
* Make body on ipad more wide


| **v1.0.8** - *20.05.1014*
| Add some small features to profile. Need database scheme update.

| ``ALTER TABLE core_gallery ADD COLUMN allow_archiving boolean NOT NULL DEFAULT true;``

* Fix bug not safe HTML_EXTRA
* Fix bug admin gallery title unique integrity error
* Add bulk time edit and update from exif actions for images in profile
* Add option to allow/disallow gallery archiving
* Add disk cache info in user profile


| **v1.0.7** - *26.01.1014*
| Fix some bugs. Move project to django 1.6

* Fix exception in getting image cache name on wrong file path
* Add year filter on sub galleries pages
* Add python 3.2 support
* Add EXTRA_HTML config variable to pass some html/js code to template


| **v1.0.6** - *3.01.1014*
| Hot critical bug fix.

* Fix bug with worker redis connection serialization


| **v1.0.5** - *3.01.1014*
| Move project to new short address. Add slideshow module. Fix too big size vertical image.
  The basis for the transition to the new rest module was more simple and clear api.

| Deployment: Run manage.py syncdb.
  Add slideshow permissions to holders to allow it in profile.
  Update requirements.

* Move project from https://bitbucket.org/b7w/believeviewer to https://bitbucket.org/b7w/bviewer
* Fix image resize feature
* Add custom scrollbar for webkit
* Move project from Tastypie to Django REST framework
* Add mock redis dependency for test purpose
* Add slideshow app


| **v1.0.4** - *10.09.1013*
| Change copyright view. Add deployment with new fabfile. Improve profile app.
  Fix some bugs and documentation.

* Update documentation to last changes
* Remake fabfile, add some features
* Fix bug when with ctrl key gallery not open in new tab
* Refactor requirements, update tastypie to v0.10.0
* Change copyright display
* Add some account fields to user profile


| **v1.0.3** - *8.08.1013*
| Improve profile site, fix some bugs. Remove link from preview to separate image view.

* Fix bug when new image allowed to add to not user gallery
* Simplified admin and profile code
* Add auto detect image path in profile
* Add image count in gallery profile
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