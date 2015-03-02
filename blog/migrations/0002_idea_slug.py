# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='idea',
            name='slug',
            field=models.SlugField(default=datetime.datetime(2014, 11, 14, 5, 7, 54, 20000, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
