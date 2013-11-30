# -*- coding: utf-8 -*-
from bviewer.api.resources import UserResource, GalleryResource, ImageResource, VideoResource
from bviewer.api.router import ExtraRouter
from bviewer.slideshow.resources import SlideShowResource


version1 = ExtraRouter()
version1.register(r'user', UserResource)
version1.register(r'gallery', GalleryResource)
version1.register(r'image', ImageResource)
version1.register(r'video', VideoResource)
version1.register(r'slideshow', SlideShowResource, base_name='slideshow')
