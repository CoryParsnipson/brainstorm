# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_idea_slug'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='idea',
            name='id',
        ),
        migrations.AlterField(
            model_name='idea',
            name='slug',
            field=models.SlugField(serialize=False, primary_key=True),
            preserve_default=True,
        ),
    ]
