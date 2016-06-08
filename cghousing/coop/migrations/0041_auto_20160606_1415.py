# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('coop', '0040_auto_20160601_1301'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParticipationRequirement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datetime_created', models.DateTimeField(default=django.utils.timezone.now, null=True, editable=False)),
                ('datetime_modified', models.DateTimeField(default=django.utils.timezone.now, null=True, editable=False)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('date', models.DateField(help_text=b'Date when the requirement occurs or when it will be assessed.')),
                ('creator', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True)),
                ('excusees', models.ManyToManyField(help_text=b'The members who are excused from fulfilling this participation requirement.', related_name='excused_participation_requirements', to='coop.Person', blank=True)),
                ('fulfillers', models.ManyToManyField(help_text=b'The members who have fulfilled this participation requirement.', related_name='fulfilled_participation_requirements', to='coop.Person', blank=True)),
                ('modifier', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True)),
                ('shirkers', models.ManyToManyField(help_text=b'The members who have shirked (not fulfilled) this participation requirement.', related_name='shirked_participation_requirements', to='coop.Person', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='applicationsettings',
            name='member_pages',
            field=models.TextField(default=b'[]', help_text='Ordered list of members only pages. Must be a JSON array of arrays, where each subarray is a 2-ary array of the form `[url, title]`.'),
            preserve_default=True,
        ),
    ]
