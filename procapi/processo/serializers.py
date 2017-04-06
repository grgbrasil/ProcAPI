# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers
from rest_framework_mongoengine import serializers as mongoserializers

from models import Processo


class ProcessoSerializer(mongoserializers.DocumentSerializer):
    numero = serializers.CharField(read_only=False)

    class Meta:
        model = Processo
        fields = '__all__'
