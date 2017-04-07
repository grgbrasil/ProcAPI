# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.generics import ListAPIView
from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_framework_mongoengine.viewsets import (
    ReadOnlyModelViewSet as MongoReadOnlyModelViewSet,
)

from .models import Evento, Parte, Processo
from .serializers import (
    ListaEventoSerializer,
    ListaParteSerializer,
    ProcessoSerializer
)


class ProcessoViewSet(NestedViewSetMixin, MongoReadOnlyModelViewSet, ):
    model = Processo
    lookup_field = 'numero'
    serializer_class = ProcessoSerializer

    def get_queryset(self):
        return Processo.objects.all()


class EventoViewSet(NestedViewSetMixin, MongoReadOnlyModelViewSet):
    model = Evento
    lookup_field = 'numero'
    serializer_class = ListaEventoSerializer

    def get_queryset(self):
        processo_numero = self.kwargs['parent_lookup_processo']
        eventos = Processo.objects.get(numero=processo_numero).eventos
        if 'numero' in self.kwargs:
            evento_numero = self.kwargs['numero']
            eventos.filter(numero=evento_numero)
        return eventos


class ParteListAPIView(ListAPIView):
    model = Parte
    serializer_class = ListaParteSerializer

    def get_queryset(self):
        processo_numero = self.kwargs['parent_lookup_processo']
        return Processo.objects.get(numero=processo_numero).partes
