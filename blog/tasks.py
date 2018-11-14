from __future__ import absolute_import, unicode_literals
from celery import shared_task

import datetime

from blog.models import Highlight

@shared_task
def publish_highlight(highlight_id):
    """ Given a Highlight id, retrieve it and set is_published to true
    """

    try:
        instance = Highlight.objects.get(id=highlight_id)

        instance.is_published = True
        instance.date_published = datetime.datetime.now()
        instance.save()

    except Highlight.DoesNotExist:
        pass
