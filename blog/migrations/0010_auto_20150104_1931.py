# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0009_auto_20150104_1905'),
    ]

    operations = [
        migrations.AlterField(
            model_name='idea',
            name='order',
            field=models.IntegerField(unique=True),
            preserve_default=True,
        ),
    ]
