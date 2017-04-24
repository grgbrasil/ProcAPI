# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import os
from celery import Celery
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.common')
app = Celery('procapi_tasks')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    enable_utc=True,
    timezone=settings.TIME_ZONE,
)

app.autodiscover_tasks()
