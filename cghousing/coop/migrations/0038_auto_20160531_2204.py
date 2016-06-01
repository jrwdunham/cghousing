# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coop', '0037_auto_20160530_1113'),
    ]

    operations = [
        migrations.AlterField(
            model_name='phonenumber',
            name='phone_type',
            field=models.CharField(max_length=10, null=True, choices=[('', ''), ('cell', 'cell'), ('home', 'home')]),
            preserve_default=True,
        ),
    ]
