# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.decorators import link
from rest_framework.filters import OrderingFilter, DjangoFilterBackend
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.relations import HyperlinkedIdentityField
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet

from bviewer.api.resources import ITEMS_PER_PAGE
from bviewer.slideshow.controllers import SlideShowController
from bviewer.slideshow.models import SlideShow


class SlideShowSerializer(ModelSerializer):
    detail = HyperlinkedIdentityField(view_name='slideshow-detail')

    class Meta:
        model = SlideShow
        exclude = ('session_key', )
        read_only_fields = ('user', 'status', 'image_count', )


class SlideShowResource(ModelViewSet):
    queryset = SlideShow.objects.all().select_related()

    http_method_names = ('get', 'post', 'delete', )
    serializer_class = SlideShowSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )

    filter_backends = (OrderingFilter, DjangoFilterBackend, )
    filter_fields = ('id', 'gallery', 'status', )
    ordering = ('gallery', 'time',)

    paginate_by = ITEMS_PER_PAGE

    def get_queryset(self):
        return self.queryset.filter(session_key=self.request.session.session_key)

    @link()
    def get_or_create(self, request, pk=None):
        if pk:
            return Response(dict(error='No "pk" parameter needed'), status=status.HTTP_400_BAD_REQUEST)
        session_key = request.session.session_key
        gallery_id = request.GET.get('gallery')
        if not gallery_id:
            return Response(dict(error='No "gallery" parameter'), status=status.HTTP_400_BAD_REQUEST)

        controller = SlideShowController(request.user, session_key, gallery_id=gallery_id)
        if not controller.get_gallery():
            return Response(dict(error='No gallery'), status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(controller.get_or_create())
        return Response(serializer.data)

    @link()
    def next(self, request, pk=None):
        if not pk:
            return Response(dict(error='No "pk" parameter'), status=status.HTTP_400_BAD_REQUEST)
        session_key = request.session.session_key

        controller = SlideShowController(request.user, session_key, slideshow_id=pk)
        if controller.get_object():
            image = controller.next_image()
            if image:
                link = reverse('core.download', args=('big', image.id,))
                return Response(dict(image_id=image.id, link=link, title=image.gallery.title))
            controller.finish()
            return Response(dict(error='No more images'), status=status.HTTP_204_NO_CONTENT)
        return Response(dict(error='No slideshow with id "{0}'.format(pk)), status=status.HTTP_404_NOT_FOUND)