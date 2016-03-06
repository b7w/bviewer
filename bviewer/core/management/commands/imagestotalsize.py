# -*- coding: utf-8 -*-
import logging

from django.core.management.base import BaseCommand

from bviewer.core.files.storage import ImageStorage
from bviewer.core.models import Gallery, Album, Image

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = 'None'
    help = 'Images total size on disk'

    class Stat:
        def __init__(self):
            self.size = 0
            self.count = 0

        def human_size(self):
            return self.size / 2 ** 20

    def size_for_gallery(self, gallery, stat):
        albums = Album.objects.filter(gallery=gallery).iterator()
        storage = ImageStorage(gallery)
        for album in albums:
            self.size_for_album(storage, album, stat)

    def size_for_album(self, storage, album, stat):
        images = Image.objects.filter(album=album).iterator()
        for image in images:
            image_path = storage.get_path(image.path)
            if image_path.exists:
                stat.size += storage.size(image.path)
                stat.count += 1

    def handle(self, *args, **options):
        stat = Command.Stat()
        galleries = Gallery.objects.iterator()
        for gallery in galleries:
            self.size_for_gallery(gallery, stat)
        self.stdout.write('Total images count: {}'.format(stat.count))
        self.stdout.write('Total images size: {:.0f} MB'.format(stat.human_size()))
