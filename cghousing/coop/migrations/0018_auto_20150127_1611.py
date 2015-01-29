# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coop', '0017_auto_20150127_1605'),
    ]

    operations = [
        migrations.AlterField(
            model_name='thread',
            name='initial_post',
            field=models.OneToOneField(related_name='parent_thread', null=True, default=None, blank=True, to='coop.Post'),
            preserve_default=True,
        ),
    ]
