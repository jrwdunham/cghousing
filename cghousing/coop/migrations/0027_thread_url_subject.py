# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coop', '0026_forum_url_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='thread',
            name='url_subject',
            field=models.CharField(default=None, max_length=200, unique=True, null=True, blank=True),
            preserve_default=True,
        ),
    ]
