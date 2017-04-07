# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework_mongoengine import serializers as mongoserializers

from .models import Evento, Processo


class ProcessoSerializer(mongoserializers.DocumentSerializer):

    class Meta:
        model = Processo
        fields = '__all__'


class ListaEventosSerializer(mongoserializers.DocumentSerializer):

    class Meta:
        model = Evento
        fields = '__all__'


