# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers
from rest_framework_mongoengine import serializers as mongoserializers

from .models import Evento, Parte, Processo


class ProcessoSerializer(mongoserializers.DocumentSerializer):

    class Meta:
        model = Processo
        fields = '__all__'


class ListaEventoSerializer(mongoserializers.DocumentSerializer):

    class Meta:
        model = Evento
        fields = '__all__'


class ListaParteSerializer(mongoserializers.DocumentSerializer):

    class Meta:
        model = Parte
        fields = '__all__'
