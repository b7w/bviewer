# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.core.validators

import django.db.models.deletion
import django.utils.timezone
from django.db import models, migrations
from django.conf import settings

import bviewer.core.models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Access',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('is_active', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Album',
            fields=[
                ('id', models.CharField(primary_key=True, max_length=32, default=bviewer.core.models.uuid_pk,
                                        serialize=False)),
                ('title', models.CharField(max_length=256)),
                ('visibility',
                 models.SmallIntegerField(default=1, choices=[(1, 'Visible'), (2, 'Hidden'), (3, 'Private')],
                                          help_text='HIDDEN - not shown on page for anonymous, PRIVATE - available only to the gallery')),
                ('album_sorting', models.SmallIntegerField(default=1, choices=[(1, 'Ascending '), (2, 'Descending')],
                                                           help_text='How to sort albums inside')),
                ('allow_archiving', models.BooleanField(default=True)),
                ('description', models.TextField(null=True, blank=True, max_length=512)),
                ('time', models.DateTimeField(default=bviewer.core.models.date_now)),
            ],
            options={
                'verbose_name_plural': 'Albums',
                'verbose_name': 'Album',
                'ordering': ['-time'],
            },
        ),
        migrations.CreateModel(
            name='Gallery',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('description', models.CharField(max_length=256)),
                ('url', models.CharField(max_length=16, unique=True)),
                ('home', models.CharField(blank=True, max_length=512, default='')),
                ('cache_size', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(16),
                                                                       django.core.validators.MaxValueValidator(512)],
                                                           default=32)),
                ('cache_archive_size', models.PositiveIntegerField(
                    validators=[django.core.validators.MinValueValidator(128),
                                django.core.validators.MaxValueValidator(2048)], default=256)),
                ('about_title', models.CharField(blank=True, max_length=256)),
                ('about_text', models.TextField(blank=True, max_length=1024)),
                ('top_album',
                 models.ForeignKey(blank=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='top',
                                   to='core.Album', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Galleries',
                'permissions': (('user_holder', 'User is gallery holder'),),
                'verbose_name': 'Gallery',
                'ordering': ['user'],
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.CharField(primary_key=True, max_length=32, default=bviewer.core.models.uuid_pk,
                                        serialize=False)),
                ('path', models.CharField(max_length=512)),
                ('time', models.DateTimeField(default=django.utils.timezone.now)),
                ('album', models.ForeignKey(to='core.Album')),
            ],
            options={
                'verbose_name': 'Image',
                'ordering': ['time'],
            },
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.CharField(primary_key=True, max_length=32, default=bviewer.core.models.uuid_pk,
                                        serialize=False)),
                ('uid', models.CharField(max_length=32)),
                ('type', models.SmallIntegerField(choices=[(2, 'YouTube'), (1, 'Vimio')], default=2)),
                ('title', models.CharField(max_length=256)),
                ('description', models.TextField(null=True, blank=True, max_length=512)),
                ('time', models.DateTimeField(default=django.utils.timezone.now)),
                ('album', models.ForeignKey(to='core.Album')),
            ],
            options={
                'verbose_name': 'Video',
                'ordering': ['time'],
            },
        ),
        migrations.AddField(
            model_name='album',
            name='gallery',
            field=models.ForeignKey(to='core.Gallery'),
        ),
        migrations.AddField(
            model_name='album',
            name='parent',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children',
                                    to='core.Album', null=True),
        ),
        migrations.AddField(
            model_name='album',
            name='thumbnail',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, related_name='thumbnail',
                                    to='core.Image', null=True),
        ),
        migrations.AddField(
            model_name='access',
            name='gallery',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='core.Gallery'),
        ),
        migrations.AddField(
            model_name='access',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='video',
            unique_together=set([('uid', 'album')]),
        ),
        migrations.AlterUniqueTogether(
            name='image',
            unique_together=set([('album', 'path')]),
        ),
        migrations.AlterUniqueTogether(
            name='album',
            unique_together=set([('title', 'gallery')]),
        ),
        migrations.AlterUniqueTogether(
            name='access',
            unique_together=set([('user', 'gallery')]),
        ),
    ]
