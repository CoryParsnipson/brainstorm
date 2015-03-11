# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0018_readinglistitem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='readinglistitem',
            name='link',
            field=models.URLField(max_length=400),
            preserve_default=True,
        ),
    ]
