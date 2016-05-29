# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coop', '0035_auto_20160529_0717'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='editable',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
