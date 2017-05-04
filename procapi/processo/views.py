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
from .tasks import atualizar_processo_desatualizado

class ProcessoViewSet(NestedViewSetMixin, MongoReadOnlyModelViewSet, ):
    model = Processo
    lookup_field = 'numero'
    serializer_class = ProcessoSerializer

    def get_queryset(self):
        return Processo.objects.all()

    def get_object(self):
        object = super(ProcessoViewSet, self).get_object()
        if object and not object.atualizado and not object.atualizando:
            object.atualizando = True
            object.save()
            atualizar_processo_desatualizado.delay(numero=object.numero)
        return object
    
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
