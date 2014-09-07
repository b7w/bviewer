# -*- coding: utf-8 -*-
import logging
from collections import defaultdict
from django.template import Template, Context
from django.core.management.base import BaseCommand

from bviewer.core.models import Gallery, Album, Image

from bviewer.core.files.storage import ImageStorage


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = 'None'
    help = 'Check that images available on storage'

    template = Template(('Detect {{ count }} images that unavailable on storage.\n'
                         '{% for name, images in report.items %}\n'
                         'Album \'{{ name }}\':\n'
                         '  {% for path in images %}'
                         '  {{ path }}\n'
                         '  {% endfor %}'
                         '{% endfor %}'))

    def check_user(self, user):
        report = defaultdict(list)
        counter = 0
        galleries = Gallery.objects.filter(user=user)
        for gallery in galleries:
            albums = Album.objects.filter(gallery=gallery).iterator()
            for album in albums:
                counter += self.check_album(gallery, album, report)
        if counter:
            user.email_user('bviewer notification', self.render(report, counter))
        return counter

    def check_album(self, gallery, album, report):
        counter = 0
        images = Image.objects.filter(album=album).iterator()
        storage = ImageStorage(gallery)
        for image in images:
            image_path = storage.get_path(image.path)
            if not image_path.exists:
                counter += 1
                report[album.title].append(image.path)
        return counter

    def handle(self, *args, **options):
        counter_all = 0
        holders = Gallery.objects.distinct('user').order_by('user').iterator()
        for user in holders:
            counter_all += self.check_user(user)
        self.stdout.write('Detect {0} unavailable images'.format(counter_all))

    def render(self, report, count):
        context = Context(dict(report=dict(report), count=count))
        return self.template.render(context)