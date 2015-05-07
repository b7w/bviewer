# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.utils.timezone
import django.db.models.deletion

import bviewer.core.models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SlideShow',
            fields=[
                ('id', models.CharField(default=bviewer.core.models.uuid_pk, serialize=False, max_length=32,
                                        primary_key=True)),
                ('session_key', models.CharField(max_length=32)),
                ('timer', models.SmallIntegerField(default=10)),
                ('status', models.SmallIntegerField(choices=[(1, 'New'), (2, 'Build'), (3, 'Finished')], default=1)),
                ('image_count', models.IntegerField(default=0)),
                ('time', models.DateTimeField(default=django.utils.timezone.now)),
                ('album', models.ForeignKey(to='core.Album', on_delete=django.db.models.deletion.DO_NOTHING)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, blank=True,
                                           on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
            options={
                'verbose_name': 'SlideShow',
                'ordering': ['time'],
            },
        ),
    ]
