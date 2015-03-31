# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0022_auto_20150322_0135'),
    ]

    operations = [
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField(max_length=1500)),
                ('date_published', models.DateTimeField(auto_now=True, auto_now_add=True)),
                ('idea', models.ManyToManyField(to='blog.Idea', null=True, blank=True)),
                ('thoughts', models.ManyToManyField(to='blog.Thought', null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField(max_length=300)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('date_due', models.DateField(null=True, blank=True)),
                ('is_completed', models.BooleanField(default=False)),
                ('priority', models.IntegerField(default=1, choices=[(0, b'Low'), (1, b'Medium'), (2, b'High'), (3, b'Next')])),
                ('idea', models.ForeignKey(blank=True, to='blog.Idea', null=True)),
                ('parent_task', models.ForeignKey(blank=True, to='blog.Task', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
