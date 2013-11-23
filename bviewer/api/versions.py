# -*- coding: utf-8 -*-
from rest_framework import routers

from bviewer.api.resources import UserResource, GalleryResource, ImageResource, VideoResource


version1 = routers.DefaultRouter()
version1.register(r'user', UserResource)
version1.register(r'gallery', GalleryResource)
version1.register(r'image', ImageResource)
version1.register(r'video', VideoResource)
