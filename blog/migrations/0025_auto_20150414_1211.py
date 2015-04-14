# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0024_auto_20150331_2228'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='priority',
            field=models.IntegerField(default=1, blank=True, choices=[(0, b'Low'), (1, b'Medium'), (2, b'High'), (3, b'Next')]),
            preserve_default=True,
        ),
    ]
