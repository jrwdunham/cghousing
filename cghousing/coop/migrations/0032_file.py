# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('coop', '0031_page_trusted'),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datetime_created', models.DateTimeField(default=django.utils.timezone.now, null=True, editable=False)),
                ('datetime_modified', models.DateTimeField(default=django.utils.timezone.now, null=True, editable=False)),
                ('name', models.IntegerField()),
                ('public', models.BooleanField(default=False)),
                ('creator', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True)),
                ('modifier', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
