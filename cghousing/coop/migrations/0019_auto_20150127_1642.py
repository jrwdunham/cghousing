# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('coop', '0018_auto_20150127_1611'),
    ]

    operations = [
        migrations.CreateModel(
            name='MeetingMinutes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datetime_created', models.DateTimeField(default=django.utils.timezone.now, null=True, editable=False)),
                ('datetime_modified', models.DateTimeField(default=django.utils.timezone.now, null=True, editable=False)),
                ('meeting_date', models.DateField()),
                ('minutes', models.TextField(blank=True)),
                ('committee', models.ForeignKey(related_name='meeting_minutes', to='coop.Committee')),
                ('creator', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True)),
                ('modifier', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='page',
            name='content',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
    ]
