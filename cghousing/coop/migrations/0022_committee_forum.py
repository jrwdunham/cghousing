# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coop', '0021_remove_thread_initial_post'),
    ]

    operations = [
        migrations.AddField(
            model_name='committee',
            name='forum',
            field=models.OneToOneField(default=None, blank=True, to='coop.Forum'),
            preserve_default=True,
        ),
    ]
