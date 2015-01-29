# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coop', '0015_auto_20150127_1356'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='thread',
            name='post',
        ),
        migrations.AddField(
            model_name='thread',
            name='initial_post',
            field=models.OneToOneField(related_name='parent_thread', default=None, to='coop.Post'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='post',
            name='reply_to',
            field=models.ForeignKey(related_name='replies', blank=True, to='coop.Post', null=True),
            preserve_default=True,
        ),
    ]
