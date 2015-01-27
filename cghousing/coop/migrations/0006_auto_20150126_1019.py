# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coop', '0005_unitinspection'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='notes',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person',
            name='phone_numbers',
            field=models.ManyToManyField(related_name='owners', to='coop.PhoneNumber', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='unit',
            name='notes',
            field=models.TextField(help_text='Notes about the unit.', blank=True),
            preserve_default=True,
        ),
    ]
