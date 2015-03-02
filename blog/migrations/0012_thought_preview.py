# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0011_idea_icon'),
    ]

    operations = [
        migrations.AddField(
            model_name='thought',
            name='preview',
            field=models.ImageField(null=True, upload_to=b'images'),
            preserve_default=True,
        ),
    ]
