# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0019_auto_20150310_2119'),
    ]

    operations = [
        migrations.AddField(
            model_name='readinglistitem',
            name='date_published',
            field=models.DateTimeField(default=datetime.datetime(2015, 3, 11, 4, 22, 7, 743000, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
