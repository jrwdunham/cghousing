# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coop', '0011_post_content'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='poster',
        ),
    ]
