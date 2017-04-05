# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.shortcuts import render

from .models import Processo


def index(request):
    import random
    randomico = random.random()

    proc = Processo.objects.create(
        numero='N.{}'.format(randomico),
        chave='Chave {}'.format(randomico),
    )
    proc.save()

    procs = Processo.objects
    return render(request, 'index.html', {'procs': procs})
