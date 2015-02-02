# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coop', '0027_thread_url_subject'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApplicationSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('coop_name', models.CharField(max_length=200)),
                ('public_pages', models.TextField(default=b'[]', help_text='Ordered list of page ids for the public pages of the site.')),
                ('member_pages', models.TextField(default=b'[]', help_text='Ordered list of page ids for the members-only pages of the site.')),
                ('news', models.TextField(default=None, help_text='News about the co-op: appears in the righthand sidebar.', null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='page',
            name='public',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='page',
            name='url_title',
            field=models.CharField(default=None, max_length=200, unique=True, null=True, blank=True),
            preserve_default=True,
        ),
    ]
