# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BlockRepresentative',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datetime_modified', models.DateTimeField(null=True, editable=False)),
                ('datetime_created', models.DateTimeField(null=True, editable=False)),
                ('block_number', models.IntegerField(max_length=4, choices=[(1701, 1701), (1703, 1703), (1715, 1715), (1739, 1739), (1747, 1747)])),
                ('role', models.CharField(max_length=30, choices=[(b'roof monitor', b'roof monitor'), (b'maintenance', b'maintenance')])),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Committee',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datetime_modified', models.DateTimeField(null=True, editable=False)),
                ('datetime_created', models.DateTimeField(null=True, editable=False)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Move',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datetime_modified', models.DateTimeField(null=True, editable=False)),
                ('datetime_created', models.DateTimeField(null=True, editable=False)),
                ('move_type', models.CharField(max_length=20, choices=[(b'move in', b'move in'), (b'move out', b'move out'), (b'internal move', b'internal move')])),
                ('move_date', models.DateField()),
                ('notes', models.TextField()),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datetime_modified', models.DateTimeField(null=True, editable=False)),
                ('datetime_created', models.DateTimeField(null=True, editable=False)),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField()),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datetime_modified', models.DateTimeField(null=True, editable=False)),
                ('datetime_created', models.DateTimeField(null=True, editable=False)),
                ('first_name', models.CharField(max_length=200)),
                ('last_name', models.CharField(max_length=200)),
                ('email', models.CharField(max_length=200)),
                ('committee_excused', models.BooleanField(default=False)),
                ('member', models.BooleanField(default=False)),
                ('notes', models.TextField()),
                ('children', models.ManyToManyField(related_name='parents', to='coop.Person')),
            ],
            options={
                'verbose_name_plural': 'People',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PhoneNumber',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datetime_modified', models.DateTimeField(null=True, editable=False)),
                ('datetime_created', models.DateTimeField(null=True, editable=False)),
                ('number', models.CharField(max_length=12)),
                ('phone_type', models.CharField(max_length=10, choices=[('', ''), ('cell', 'cell'), ('home', 'home')])),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datetime_modified', models.DateTimeField(null=True, editable=False)),
                ('datetime_created', models.DateTimeField(null=True, editable=False)),
                ('block_number', models.IntegerField(max_length=4, choices=[(1701, 1701), (1703, 1703), (1715, 1715), (1739, 1739), (1747, 1747)])),
                ('unit_number', models.IntegerField(max_length=3, choices=[(101, 101), (102, 102), (103, 103), (104, 104), (105, 105), (106, 106), (107, 107), (108, 108), (109, 109), (110, 110), (111, 111), (112, 112), (113, 113)])),
                ('notes', models.TextField()),
                ('bedrooms', models.IntegerField(max_length=1, choices=[(1, 1), (2, 2), (3, 3), (4, 4)])),
                ('bathrooms', models.IntegerField(max_length=1, choices=[(1, 1), (2, 2), (3, 3), (4, 4)])),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='person',
            name='phone_numbers',
            field=models.ManyToManyField(related_name='owners', to='coop.PhoneNumber'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='person',
            name='unit',
            field=models.ForeignKey(related_name='occupants', to='coop.Unit', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='move',
            name='in_unit',
            field=models.ForeignKey(related_name='move_ins', to='coop.Unit', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='move',
            name='movers',
            field=models.ManyToManyField(to='coop.Person'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='move',
            name='out_unit',
            field=models.ForeignKey(related_name='move_outs', to='coop.Unit', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='committee',
            name='chair',
            field=models.ForeignKey(related_name='chairships', to='coop.Person', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='committee',
            name='members',
            field=models.ManyToManyField(related_name='committees', to='coop.Person'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='blockrepresentative',
            name='committee',
            field=models.ForeignKey(related_name='block_representatives', to='coop.Committee', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='blockrepresentative',
            name='person',
            field=models.ForeignKey(related_name='block_representative_roles', to='coop.Person', null=True),
            preserve_default=True,
        ),
    ]
