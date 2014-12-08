# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_auto_20141115_0031'),
    ]

    operations = [
        migrations.AddField(
            model_name='idea',
            name='ordering',
            field=models.IntegerField(unique=True, null=True),
            preserve_default=True,
        ),
    ]
