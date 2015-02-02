# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coop', '0030_auto_20150201_1935'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='trusted',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
