import multiprocessing

from django.conf import settings
from django.core.management import BaseCommand
from django.core.wsgi import get_wsgi_application
from gunicorn.app.base import BaseApplication


def number_of_workers():
    return (multiprocessing.cpu_count() * 2) + 1


class StandaloneApplication(BaseApplication):
    def __init__(self):
        super(StandaloneApplication, self).__init__()

    def load_config(self):
        self.cfg.set('bind', getattr(settings, 'BIND_ADDRESS', '0.0.0.0:8000'))
        self.cfg.set('workers', number_of_workers())

    def load(self):
        return get_wsgi_application()


class Command(BaseCommand):
    help = 'Run http server'

    def handle(self, *args, **options):
        StandaloneApplication().run()
