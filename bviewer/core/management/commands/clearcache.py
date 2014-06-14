# -*- coding: utf-8 -*-
import logging

from django.core.management.base import BaseCommand

from bviewer.core.files.proxy import ProxyImageStorage
from bviewer.core.models import Gallery


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = 'None'
    help = 'Clear old links and delete old files if size of user cache is bigger'

    def handle(self, *args, **options):
        full = 'full' in args
        for user in Gallery.objects.all():
            ProxyImageStorage(user).clear_cache(full=full)
            ProxyImageStorage(user, archive_cache=True).clear_cache(full=full)
        self.stdout.write('Clear cache for {c} users'.format(c=Gallery.objects.count()))