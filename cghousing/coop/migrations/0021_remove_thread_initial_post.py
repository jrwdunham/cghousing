# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coop', '0020_auto_20150127_2152'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='thread',
            name='initial_post',
        ),
    ]
