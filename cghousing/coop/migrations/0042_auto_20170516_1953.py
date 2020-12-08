# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coop', '0041_auto_20160606_1415'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participationrequirement',
            name='excusees',
            field=models.ManyToManyField(help_text=b"The members who are excused from fulfilling this participation requirement. <a class='select-all-excusees' href='javascript:void(0)'>Select All</a> / <a class='deselect-all-excusees' href='javascript:void(0)'>De-select All</a>.", related_name='excused_participation_requirements', to='coop.Person', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='participationrequirement',
            name='fulfillers',
            field=models.ManyToManyField(help_text=b"The members who have fulfilled this participation requirement. <a class='select-all-fulfillers' href='javascript:void(0)'>Select All</a> / <a class='deselect-all-fulfillers' href='javascrip:void(0)'>De-select All</a>.", related_name='fulfilled_participation_requirements', to='coop.Person', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='participationrequirement',
            name='shirkers',
            field=models.ManyToManyField(help_text=b"The members who have shirked (not fulfilled) this participation requirement. <a class='select-all-shirkers' href='javascript:void(0)'>Select All</a> / <a class='deselect-all-shirkers' href='javascript:void(0)'>De-select All</a>.", related_name='shirked_participation_requirements', to='coop.Person', blank=True),
            preserve_default=True,
        ),
    ]
