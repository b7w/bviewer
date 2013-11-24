# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.http import Http404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.fields import IntegerField, BooleanField, CharField
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import ViewSet

from bviewer.core.models import Image
from bviewer.slideshow.controllers import SlideShowController
from bviewer.slideshow.models import SlideShow


class SlideShowSerializer(Serializer):
    gallery_id = CharField(required=True)
    timer = IntegerField(required=False)
    repeat = BooleanField(required=False)

    def restore_object(self, attrs, instance=None):
        if instance is not None:
            instance.timer = attrs.get('gallery_id', instance.gallery_id)
            instance.timer = attrs.get('timer', instance.timer)
            instance.repeat = attrs.get('repeat', instance.repeat)
            return instance
        return SlideShow(**attrs)


class SlideShowResource(ViewSet):
    serializer_class = SlideShowSerializer

    def list(self, request):
        controller = SlideShowController(request.session)
        if controller:
            serializer = SlideShowSerializer(controller.list(), many=True)
            return Response(serializer.data)
        return Response()

    def create(self, request):
        serializer = SlideShowSerializer(data=request.DATA)
        if serializer.is_valid():
            controller = SlideShowController(request.session)
            controller.add(serializer.object)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        controller = SlideShowController(request.session)
        slideshow = controller.get(gallery_id=pk)
        if slideshow:
            serializer = SlideShowSerializer(slideshow)
            return Response(serializer.data)
        raise Http404("No slideshow")

    @action(methods=('GET',))
    def next(self, request, pk=None):
        controller = SlideShowController(request.session)
        image_id = controller.next_image_id(gallery_id=pk)

        try:
            image = Image.objects.select_related().get(id=image_id)
            link = reverse('core.download', args=('big', image_id,))
            return Response(dict(image_id=image_id, link=link, title=image.gallery.title))
        except Image.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


    def update(self, request, pk=None):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def partial_update(self, request, pk=None):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def destroy(self, request, pk=None):
        controller = SlideShowController(request.session)
        controller.delete(gallery_id=pk)
        return Response()