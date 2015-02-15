# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0016_auto_20150215_1132'),
    ]

    operations = [
        migrations.AlterField(
            model_name='highlight',
            name='description',
            field=models.TextField(max_length=1500),
            preserve_default=True,
        ),
    ]
