# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0008_auto_20150103_2306'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='idea',
            name='ordering',
        ),
        migrations.AddField(
            model_name='idea',
            name='order',
            field=models.IntegerField(unique=True, null=True),
            preserve_default=True,
        ),
    ]
