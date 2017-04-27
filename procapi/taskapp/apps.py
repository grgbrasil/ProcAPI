# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.apps import AppConfig
from .celery import app as celery_app

__all__ = ['celery_app']

class TaskAppConfig(AppConfig):
    name = 'procapi.taskapp'
