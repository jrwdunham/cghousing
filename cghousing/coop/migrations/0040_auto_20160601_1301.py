# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coop', '0039_auto_20160601_1215'),
    ]

    operations = [
        migrations.AddField(
            model_name='committee',
            name='page_content',
            field=models.TextField(help_text=b"Use <a class='markdown-help' href='javascript:void(0)'>Markdown</a> to add formatting, links and images to this committee's page.", blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='committee',
            name='url_name',
            field=models.CharField(default=None, max_length=200, unique=True, null=True, blank=True),
            preserve_default=True,
        ),
    ]
