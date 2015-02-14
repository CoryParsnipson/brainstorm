# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0013_auto_20150114_2358'),
    ]

    operations = [
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=300)),
                ('description', models.CharField(max_length=500)),
                ('url', models.URLField(max_length=1000)),
                ('icon', models.ImageField(null=True, upload_to=b'images', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
