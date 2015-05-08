# -*- coding: utf-8 -*-
import logging

from django.contrib.auth.models import User, Permission

from django.core.management.base import BaseCommand

from bviewer.core.models import Gallery


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Create admin and demo user with password "root" for vagrant demo installation'

    def create_admin(self):
        admin = User.objects.filter(username='admin').first()
        if admin:
            self.stdout.write('Admin user exists')
        else:
            User.objects.create_superuser('admin', 'admin@bviewer.loc', password='root')
            self.stdout.write('Create admin user')

    def create_user(self):
        user = User.objects.filter(username='demo').first()
        if user:
            self.stdout.write('Demo user exists')
        else:
            user = User.objects.create_user('demo', 'demo@bviewer.loc', password='root')

            perm = Permission.objects.get(codename='user_holder')
            user.user_permissions.add(perm)
            user.save()

            Gallery.objects.create(user=user, url='4.4.4.4', home='', about_title='Demo gallery',
                                   about_text='About text', description='Demo preview of bviewer gallery!')
            self.stdout.write('Create demo user and demo gallery')

    def handle(self, *args, **options):
        self.create_admin()
        self.create_user()
