# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coop', '0029_auto_20150201_1838'),
    ]

    operations = [
        migrations.AddField(
            model_name='applicationsettings',
            name='home_page',
            field=models.ForeignKey(default=None, blank=True, to='coop.Page', help_text='The home page of this application.', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='applicationsettings',
            name='member_pages',
            field=models.TextField(default=b'[]', help_text='Ordered list of page ids for the members-only pages of the site: JSON array of integers.'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='applicationsettings',
            name='news',
            field=models.TextField(default='', help_text='News about the unit.', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='applicationsettings',
            name='public_pages',
            field=models.TextField(default=b'[]', help_text='Ordered list of page ids for the public pages of the site: JSON array of integers.'),
            preserve_default=True,
        ),
    ]
