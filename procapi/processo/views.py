# -*- coding: utf-8 -*-


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
        processo = Processo.objects.filter(numero=processo_numero).first()
        if processo:
            if 'numero' in self.kwargs:
                return processo.eventos.filter(numero=self.kwargs['numero'])
            return processo.eventos
        return []


class ParteListAPIView(ListAPIView):
    model = Parte
    serializer_class = ListaParteSerializer

    def get_queryset(self):
        processo_numero = self.kwargs['parent_lookup_processo']
        processo = Processo.objects.filter(numero=processo_numero).first()
        if processo:
            return processo.partes
        return []
