# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0027_auto_20150417_2332'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 20, 6, 41, 56, 490000, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='activity',
            name='tokens',
            field=models.CharField(max_length=2000, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='activity',
            name='type',
            field=models.IntegerField(default=0, choices=[(0, b'Create Idea'), (1, b'Deleted Idea'), (2, b'Started Draft'), (3, b'Published Draft'), (4, b'Trashed Draft'), (5, b'Create Thought'), (6, b'Unpublished Thought'), (7, b'Trashed Thought'), (8, b'Deleted Thought'), (9, b'Added Book to Recently Read List'), (10, b'Added Book to Wish List'), (11, b'Deleted Book'), (12, b'Added New Task Item'), (13, b'Deleted Task Item'), (14, b'Marked Task Item as Completed'), (15, b'Changed Task Priority'), (16, b'Started New Note'), (17, b'Deleted Note'), (18, b'Tweet')]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='activity',
            name='url',
            field=models.URLField(max_length=500, null=True, blank=True),
            preserve_default=True,
        ),
    ]
