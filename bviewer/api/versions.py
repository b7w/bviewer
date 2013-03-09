# -*- coding: utf-8 -*-

from tastypie.api import Api

from bviewer.api.resources import UserResource, GalleryResource, ImageResource, VideoResource


version1 = Api(api_name='v1')
version1.register(UserResource())
version1.register(GalleryResource())
version1.register(ImageResource())
version1.register(VideoResource())
