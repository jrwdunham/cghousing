# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coop', '0024_auto_20150130_1311'),
    ]

    operations = [
        migrations.AddField(
            model_name='thread',
            name='views',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
