# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coop', '0016_auto_20150127_1529'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='thread',
            field=models.ForeignKey(related_name='posts', default=None, blank=True, to='coop.Thread', null=True),
            preserve_default=True,
        ),
    ]
