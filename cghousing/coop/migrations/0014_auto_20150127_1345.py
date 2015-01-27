# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coop', '0013_auto_20150127_1340'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='replyee',
            new_name='reply_to',
        ),
    ]
