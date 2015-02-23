# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0012_thought_preview'),
    ]

    operations = [
        migrations.AlterField(
            model_name='thought',
            name='preview',
            field=models.ImageField(null=True, upload_to=b'images', blank=True),
            preserve_default=True,
        ),
    ]
