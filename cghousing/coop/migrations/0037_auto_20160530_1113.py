# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coop', '0036_page_editable'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='page_content',
            field=models.TextField(help_text=b"Use <a href='https://daringfireball.net/projects/markdown/'>Markdown</a> to add formatting, links and images to your page.", blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='page',
            name='content',
            field=models.TextField(help_text=b"Use <a href='https://daringfireball.net/projects/markdown/'>Markdown</a> to add formatting, links and images to your page.", blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='page',
            name='editable',
            field=models.BooleanField(default=False, help_text=b'If checked, then all members can edit this page. If unchecked, only its creator can edit it.'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='page',
            name='public',
            field=models.BooleanField(default=False, help_text=b'If checked, then everybody can view this page. If unchecked, only members can view it.'),
            preserve_default=True,
        ),
    ]
