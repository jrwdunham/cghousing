# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('coop', '0008_auto_20150126_1446'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='user',
            field=models.OneToOneField(null=True, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='committee',
            name='chair',
            field=models.ForeignKey(related_name='chairships', blank=True, to='coop.Person', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='committee',
            name='description',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='committee',
            name='members',
            field=models.ManyToManyField(related_name='committees', to='coop.Person', blank=True),
            preserve_default=True,
        ),
    ]
