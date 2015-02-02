# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coop', '0025_thread_views'),
    ]

    operations = [
        migrations.AddField(
            model_name='forum',
            name='url_name',
            field=models.CharField(default=None, max_length=200, unique=True, null=True, blank=True),
            preserve_default=True,
        ),
    ]
