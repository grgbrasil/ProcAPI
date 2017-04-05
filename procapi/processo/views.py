# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.shortcuts import render

from .models import Processo


def index(request):
    from random import randint
    from datetime import datetime

    proc = Processo.objects.create(
        numero='N.{:%M%S%f}'.format(datetime.now()),
        chave='Chave {}'.format('1111111'),
    )
    proc.save()

    procs = Processo.objects
    return render(request, 'index.html', {'procs': procs})
