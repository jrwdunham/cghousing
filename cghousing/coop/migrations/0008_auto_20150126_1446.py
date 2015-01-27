# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('coop', '0007_auto_20150126_1055'),
    ]

    operations = [
        migrations.CreateModel(
            name='Forum',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datetime_created', models.DateTimeField(default=django.utils.timezone.now, null=True, editable=False)),
                ('datetime_modified', models.DateTimeField(default=django.utils.timezone.now, null=True, editable=False)),
                ('name', models.CharField(unique=True, max_length=200)),
                ('description', models.TextField(blank=True)),
                ('creator', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True)),
                ('modifier', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datetime_created', models.DateTimeField(default=django.utils.timezone.now, null=True, editable=False)),
                ('datetime_modified', models.DateTimeField(default=django.utils.timezone.now, null=True, editable=False)),
                ('subject', models.CharField(max_length=200)),
                ('creator', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True)),
                ('modifier', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True)),
                ('poster', models.ForeignKey(related_name='posts', to='coop.Person')),
                ('replyee', models.ForeignKey(related_name='replies', to='coop.Post', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Thread',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datetime_created', models.DateTimeField(default=django.utils.timezone.now, null=True, editable=False)),
                ('datetime_modified', models.DateTimeField(default=django.utils.timezone.now, null=True, editable=False)),
                ('subject', models.CharField(max_length=200)),
                ('creator', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True)),
                ('modifier', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True)),
                ('poster', models.ForeignKey(related_name='threads', to='coop.Person')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='post',
            name='thread',
            field=models.ForeignKey(related_name='posts', to='coop.Thread'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='blockrepresentative',
            name='creator',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='blockrepresentative',
            name='modifier',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='committee',
            name='creator',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='committee',
            name='modifier',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='move',
            name='creator',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='move',
            name='modifier',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='page',
            name='creator',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='page',
            name='modifier',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='person',
            name='creator',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='person',
            name='modifier',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='phonenumber',
            name='creator',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='phonenumber',
            name='modifier',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='unit',
            name='creator',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='unit',
            name='modifier',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='unitinspection',
            name='creator',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='unitinspection',
            name='modifier',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='blockrepresentative',
            name='datetime_created',
            field=models.DateTimeField(default=django.utils.timezone.now, null=True, editable=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='blockrepresentative',
            name='datetime_modified',
            field=models.DateTimeField(default=django.utils.timezone.now, null=True, editable=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='committee',
            name='datetime_created',
            field=models.DateTimeField(default=django.utils.timezone.now, null=True, editable=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='committee',
            name='datetime_modified',
            field=models.DateTimeField(default=django.utils.timezone.now, null=True, editable=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='move',
            name='datetime_created',
            field=models.DateTimeField(default=django.utils.timezone.now, null=True, editable=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='move',
            name='datetime_modified',
            field=models.DateTimeField(default=django.utils.timezone.now, null=True, editable=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='page',
            name='datetime_created',
            field=models.DateTimeField(default=django.utils.timezone.now, null=True, editable=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='page',
            name='datetime_modified',
            field=models.DateTimeField(default=django.utils.timezone.now, null=True, editable=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='page',
            name='title',
            field=models.CharField(unique=True, max_length=200),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person',
            name='committee_excused',
            field=models.BooleanField(default=False, help_text='If set to true, then this person is excused from the requirement that all members belong to at least one committee.'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person',
            name='datetime_created',
            field=models.DateTimeField(default=django.utils.timezone.now, null=True, editable=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person',
            name='datetime_modified',
            field=models.DateTimeField(default=django.utils.timezone.now, null=True, editable=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person',
            name='member',
            field=models.BooleanField(default=False, help_text=b'Is this person a member of the co-op?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='phonenumber',
            name='datetime_created',
            field=models.DateTimeField(default=django.utils.timezone.now, null=True, editable=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='phonenumber',
            name='datetime_modified',
            field=models.DateTimeField(default=django.utils.timezone.now, null=True, editable=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='unit',
            name='datetime_created',
            field=models.DateTimeField(default=django.utils.timezone.now, null=True, editable=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='unit',
            name='datetime_modified',
            field=models.DateTimeField(default=django.utils.timezone.now, null=True, editable=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='unitinspection',
            name='datetime_created',
            field=models.DateTimeField(default=django.utils.timezone.now, null=True, editable=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='unitinspection',
            name='datetime_modified',
            field=models.DateTimeField(default=django.utils.timezone.now, null=True, editable=False),
            preserve_default=True,
        ),
    ]
