from __future__ import absolute_import, unicode_literals
from celery import shared_task
from celery import Celery

app = Celery('procapi_tasks')
app.config_from_object('django.conf:settings', namespace='CELERY')

@shared_task
def add(x, y):
    return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)
# celery -A procapi_task worker -l info
