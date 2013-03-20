Believe Viewer
==============

It is simple photo gallery, with simple but nice dark style. With sub albums,
and vimio/youtube video support. There are no comments or ratting, even upload.
Gallery can be make private, to be shown only for owner. It is multi user app,
each gallery holder need to have sub domain, *user.domain.com*.

*This app is not ready for usage*


Sum fetches
-----------

 * Multi user
 * Sub albums
 * Slide show
 * Video support
 * Private galleries
 * Nice dark template :-)
 * Download full images in zip archive


Technologies
------------

 * Django, PostgerSQL or any other.
 * Celery, plus Redis DB. But can be other.
 * Bootstrap


Install
-------
To install Postgres driver and image library via ubuntu apt `sudo apt-get install python-psycopg2 python-imaging`.
Or build with pip - recommended, at least pillow.

* Postgres driver
    * `sudo apt-get install libpq-dev python-dev libjpeg-dev libfreetype6-dev zlib1g-dev;`
    * `sudo pip install psycopg2`
* Pillow - Imaging Library fork that in active development
    * `sudo apt-get install python-dev libjpeg-dev libfreetype6-dev zlib1g-dev;`
    * `sudo pip install pillow`

Other python libraries `sudo pip install -r requirements.txt`.
