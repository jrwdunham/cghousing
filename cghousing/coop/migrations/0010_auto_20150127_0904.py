# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coop', '0009_auto_20150126_1649'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='thread',
            name='poster',
        ),
        migrations.AddField(
            model_name='thread',
            name='forum',
            field=models.ForeignKey(related_name='threads', default=None, to='coop.Forum', null=True),
            preserve_default=True,
        ),
    ]
