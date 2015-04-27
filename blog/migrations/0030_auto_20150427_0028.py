# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0029_auto_20150426_1621'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='type',
            field=models.IntegerField(choices=[(0, b'Create Idea'), (1, b'Edited Idea'), (2, b'Deleted Idea'), (3, b'Started Draft'), (4, b'Published Draft'), (5, b'Edited Draft'), (6, b'Moved Draft'), (7, b'Trashed Draft'), (8, b'Untrashed Draft'), (9, b'Deleted Draft'), (10, b'Published Thought'), (11, b'Unpublished Thought'), (12, b'Edited Thought'), (13, b'Moved Thought'), (14, b'Trashed Thought'), (15, b'Untrashed Thought'), (16, b'Deleted Thought'), (17, b'Added New Highlight'), (18, b'Edited Highlight'), (19, b'Deleted Highlight'), (20, b'Added Book to Recently Read List'), (21, b'Added Book to Wish List'), (22, b'Edited Book'), (23, b'Moved Book to Recently Read List'), (24, b'Deleted Book'), (25, b'Added New Task Item'), (26, b'Edited Task Item'), (27, b'Deleted Task Item'), (28, b'Marked Task Item as Completed'), (29, b'Changed Task Priority'), (30, b'Started New Note'), (31, b'Edited Note'), (32, b'Deleted Note'), (33, b'Tweet')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='note',
            name='title',
            field=models.CharField(max_length=500),
            preserve_default=True,
        ),
    ]
