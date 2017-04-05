# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from mixer.backend.mongoengine import Mixer
from mongoengine import *

from procapi.processo.models import Processo


class TestProcesso:

    mixer = Mixer(commit=False)
    processo_obj = mixer.blend(Processo)
    processo_attr = [
        'id',
        'numero',
        'chave',
    ]

    processo = mixer.blend(Processo, numero='12345')

    def test_quantidade_atributos(self):
        assert self.processo_obj.__len__() == 3

    def test_atributos_existentes(self):
        for att in self.processo_attr:
            assert hasattr(Processo(), att)

    def test_processo_numero_valido(self):
        assert self.processo.numero
