# -*- coding: utf-8 -*-
import logging

from django.core.management.base import BaseCommand

from bviewer.core.files.storage import ImageStorage
from bviewer.core.models import ProxyUser


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = 'None'
    help = 'Clear old links and delete old files if size of user cache is bigger'

    def handle(self, *args, **options):
        for user in ProxyUser.objects.all():
            ImageStorage(user).clear_cache()
            ImageStorage(user, archive_cache=True).clear_cache()
        self.stdout.write('Clear cache for {c} users'.format(c=ProxyUser.objects.count()))