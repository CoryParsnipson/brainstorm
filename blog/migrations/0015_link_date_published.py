# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0014_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='link',
            name='date_published',
            field=models.DateTimeField(default=datetime.datetime(2015, 2, 13, 22, 13, 40, 824000, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
