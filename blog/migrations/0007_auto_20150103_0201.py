# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0006_thought_is_draft'),
    ]

    operations = [
        migrations.AddField(
            model_name='thought',
            name='is_trash',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='thought',
            name='is_draft',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
