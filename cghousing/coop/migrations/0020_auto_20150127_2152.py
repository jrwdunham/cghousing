# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coop', '0019_auto_20150127_1642'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='meetingminutes',
            options={'verbose_name_plural': 'Meeting minutes'},
        ),
    ]
