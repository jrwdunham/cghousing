# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coop', '0006_auto_20150126_1019'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='children',
            field=models.ManyToManyField(related_name='parents', to='coop.Person', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person',
            name='email',
            field=models.CharField(max_length=200, blank=True),
            preserve_default=True,
        ),
    ]
