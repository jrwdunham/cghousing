# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coop', '0038_auto_20160531_2204'),
    ]

    operations = [
        migrations.AddField(
            model_name='unit',
            name='page_content',
            field=models.TextField(help_text=b"Use <a class='markdown-help' href='javascript:void(0)'>Markdown</a> to add formatting, links and images to your unit's page.", blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='page',
            name='content',
            field=models.TextField(help_text=b"Use <a class='markdown-help' href='javascript:void(0)'>Markdown</a> to add formatting, links and images to your page.", blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person',
            name='page_content',
            field=models.TextField(help_text=b"Use <a class='markdown-help' href='javascript:void(0)'>Markdown</a> to add formatting, links and images to your page.", blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='phonenumber',
            name='phone_type',
            field=models.CharField(blank=True, max_length=10, null=True, choices=[('', ''), ('cell', 'cell'), ('home', 'home')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='post',
            name='post',
            field=models.TextField(help_text=b"Use <a class='markdown-help' href='javascript:void(0)'>Markdown</a> to add formatting, links and images to your post."),
            preserve_default=True,
        ),
    ]
