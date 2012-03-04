# -*- coding: utf-8 -*-

from django.contrib import admin
from models import Gallery, Image, Video

class GalleryAdmin( admin.ModelAdmin ):
    pass

admin.site.register( Gallery, GalleryAdmin )


class ImageAdmin( admin.ModelAdmin ):
    pass

admin.site.register( Image, ImageAdmin )

class VideoAdmin( admin.ModelAdmin ):
    pass

admin.site.register( Video, VideoAdmin )
