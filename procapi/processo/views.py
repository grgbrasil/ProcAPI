# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from rest_framework import viewsets
from rest_framework_mongoengine.viewsets import ModelViewSet as MongoModelViewSet
from rest_framework_extensions.mixins import NestedViewSetMixin

from models import Processo
from serializers import ProcessoSerializer

class ProcessoViewSet(MongoModelViewSet):
    model = Processo
    lookup_field = 'numero'
    serializer_class = ProcessoSerializer

    def get_queryset(self):
        return Processo.objects.all()
