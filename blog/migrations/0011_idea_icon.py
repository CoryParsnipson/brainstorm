# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0010_auto_20150104_1931'),
    ]

    operations = [
        migrations.AddField(
            model_name='idea',
            name='icon',
            field=models.ImageField(default='images/idea_icon_default.png', upload_to=b'images'),
            preserve_default=False,
        ),
    ]
