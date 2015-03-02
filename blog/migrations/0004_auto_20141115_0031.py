# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_auto_20141115_0012'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='thought',
            name='id',
        ),
        migrations.AlterField(
            model_name='thought',
            name='slug',
            field=models.SlugField(serialize=False, primary_key=True),
            preserve_default=True,
        ),
    ]
