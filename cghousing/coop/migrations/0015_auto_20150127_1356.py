# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coop', '0014_auto_20150127_1345'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='content',
            new_name='post',
        ),
        migrations.AddField(
            model_name='thread',
            name='post',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
