# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coop', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unit',
            name='bathrooms',
            field=models.IntegerField(default=0, max_length=1, null=True, blank=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='unit',
            name='bedrooms',
            field=models.IntegerField(default=0, max_length=1, null=True, blank=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='unit',
            name='notes',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
    ]
