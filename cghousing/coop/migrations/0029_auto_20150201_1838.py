# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('coop', '0028_auto_20150201_1833'),
    ]

    operations = [
        migrations.AddField(
            model_name='applicationsettings',
            name='creator',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='applicationsettings',
            name='datetime_created',
            field=models.DateTimeField(default=django.utils.timezone.now, null=True, editable=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='applicationsettings',
            name='datetime_modified',
            field=models.DateTimeField(default=django.utils.timezone.now, null=True, editable=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='applicationsettings',
            name='modifier',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='applicationsettings',
            name='coop_name',
            field=models.CharField(default='Co-op', max_length=200),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='applicationsettings',
            name='news',
            field=models.TextField(default='', help_text='Notes about the unit.', null=True, blank=True),
            preserve_default=True,
        ),
    ]
