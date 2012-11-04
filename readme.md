Believe Viewer
==============

It is simple photo gallery, with simple but nice dark style. With sub albums,
and vimio/youtube video support. There are no comments or ratting, even upload.
Gallery can be make private, to be shown only for owner. It is multi user app,
each gallery holder need to have sub domain, *user.domain.com*.

As I said there is no upload. Images have to stored in server folder, where app can take it.
On page load images resizing and putting to cache. Cache size can be changed.
I made it because app run on server where images stored, a lot of images.
I don' want to duplicate them.

But, nice outside, it is terrible management inside. Adding and managing galleries
is far away from right way. *I still think how to fix this*.

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