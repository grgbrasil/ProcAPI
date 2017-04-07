# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_framework_mongoengine.viewsets import (
    ReadOnlyModelViewSet as MongoReadOnlyModelViewSet,
)

from .models import Evento, Processo
from .serializers import (
    ListaEventosSerializer,
    ProcessoSerializer
)


class ProcessoViewSet(NestedViewSetMixin, MongoReadOnlyModelViewSet, ):
    model = Processo
    lookup_field = 'numero'
    serializer_class = ProcessoSerializer

    def get_queryset(self):
        return Processo.objects.all()


class EventosViewSet(NestedViewSetMixin, MongoReadOnlyModelViewSet):
    model = Evento
    lookup_field = 'numero'
    serializer_class = ListaEventosSerializer

    def get_queryset(self):
        processo_numero = self.kwargs['parent_lookup_processo']
        eventos = Processo.objects.get(numero=processo_numero).eventos
        if 'numero' in self.kwargs:
            evento_numero = self.kwargs['numero']
            eventos.filter(numero=evento_numero)
        return eventos
