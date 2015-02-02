# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coop', '0023_auto_20150130_1310'),
    ]

    operations = [
        migrations.AlterField(
            model_name='committee',
            name='forum',
            field=models.OneToOneField(related_name='committee', null=True, default=None, blank=True, to='coop.Forum'),
            preserve_default=True,
        ),
    ]
