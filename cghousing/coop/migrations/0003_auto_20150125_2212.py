# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coop', '0002_auto_20150125_2210'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unit',
            name='bathrooms',
            field=models.IntegerField(default=1, max_length=1, choices=[(1, 1), (2, 2), (3, 3), (4, 4)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='unit',
            name='bedrooms',
            field=models.IntegerField(default=3, max_length=1, choices=[(1, 1), (2, 2), (3, 3), (4, 4)]),
            preserve_default=True,
        ),
    ]
