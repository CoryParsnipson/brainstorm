# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0007_auto_20150103_0201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='idea',
            name='ordering',
            field=models.IntegerField(unique=True),
            preserve_default=True,
        ),
    ]
