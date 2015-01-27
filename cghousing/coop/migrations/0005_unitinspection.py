# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coop', '0004_auto_20150125_2219'),
    ]

    operations = [
        migrations.CreateModel(
            name='UnitInspection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datetime_modified', models.DateTimeField(null=True, editable=False)),
                ('datetime_created', models.DateTimeField(null=True, editable=False)),
                ('date', models.DateField()),
                ('request_date', models.DateField(null=True)),
                ('content', models.TextField(blank=True)),
                ('requester', models.ForeignKey(related_name='requested_inspections', to='coop.Person', null=True)),
                ('unit', models.ForeignKey(related_name='inspections', to='coop.Unit')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
