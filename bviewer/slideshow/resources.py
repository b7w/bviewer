# -*- coding: utf-8 -*-
from django.http import Http404
from rest_framework import status
from rest_framework.fields import IntegerField, BooleanField, CharField
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import ViewSet

from bviewer.slideshow.controllers import SlideShowController


class SlideShow(object):
    def __init__(self, uid, timer=10, repeat=True):
        self.uid = uid
        self.timer = timer
        self.repeat = repeat


class SlideShowSerializer(Serializer):
    uid = CharField(required=False)
    timer = IntegerField(required=False)
    repeat = BooleanField(required=False)

    def restore_object(self, attrs, instance=None):
        if instance is not None:
            instance.timer = attrs.get('timer', instance.timer)
            instance.repeat = attrs.get('repeat', instance.repeat)
            return instance
        attrs['uid'] = SlideShowController.new_key()
        return SlideShow(**attrs)


class SlideShowResource(ViewSet):
    serializer_class = SlideShowSerializer

    def list(self, request):
        slideshow = request.session.get('slideshow')
        if slideshow:
            serializer = SlideShowSerializer(slideshow)
            return Response([serializer.data, ])
        return Response()

    def create(self, request):
        serializer = SlideShowSerializer(data=request.DATA)
        if serializer.is_valid():
            request.session['slideshow'] = serializer.object
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        slideshow = request.session.get('slideshow')
        if slideshow:
            serializer = SlideShowSerializer(slideshow)
            return Response(serializer.data)
        raise Http404("No slideshow")

    def update(self, request, pk=None):
        slideshow = request.session['slideshow']
        serializer = SlideShowSerializer(instance=slideshow, data=request.DATA)
        if serializer.is_valid():
            request.session['slideshow'] = serializer.object
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        return Response(status.HTTP_501_NOT_IMPLEMENTED)

    def destroy(self, request, pk=None):
        if 'slideshow' in request.session:
            del request.session['slideshow']
        return Response()