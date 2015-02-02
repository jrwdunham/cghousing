# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coop', '0022_committee_forum'),
    ]

    operations = [
        migrations.AlterField(
            model_name='committee',
            name='forum',
            field=models.OneToOneField(null=True, default=None, blank=True, to='coop.Forum'),
            preserve_default=True,
        ),
    ]
