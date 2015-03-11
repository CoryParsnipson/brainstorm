# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0020_readinglistitem_date_published'),
    ]

    operations = [
        migrations.AlterField(
            model_name='readinglistitem',
            name='cover',
            field=models.URLField(max_length=400),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='readinglistitem',
            name='description',
            field=models.CharField(max_length=200, null=True, blank=True),
            preserve_default=True,
        ),
    ]
