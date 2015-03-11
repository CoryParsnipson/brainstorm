# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0017_auto_20150215_1153'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReadingListItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=150)),
                ('author', models.CharField(max_length=150)),
                ('link', models.URLField()),
                ('description', models.CharField(max_length=500)),
                ('wishlist', models.BooleanField(default=False)),
                ('favorite', models.BooleanField(default=False)),
                ('cover', models.URLField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
