# -*- coding: utf-8 -*-
import logging
from django.contrib.auth.models import User
from django.db import transaction

from bviewer.core.models import Access


logger = logging.getLogger(__name__)


class UserDao:
    @transaction.atomic
    def create_gallery_user(self, gallery, username, email, password):
        user = User(username=username, email=email, is_active=False)
        user.set_password(password)
        user.save()
        Access.objects.create(user=user, gallery=gallery)
        return user


user_dao = UserDao()