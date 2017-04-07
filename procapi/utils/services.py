# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import re

from suds.client import Client

from django.conf import settings

class ConsultaEProc(object):
    """Consulta Processual E-Proc"""

    GRAU_1 = 1
    GRAU_2 = 2

    resposta = None
    sucesso = None
    mensagem = None

    def numero_puro(self, numero):
        """Método que formata o numero do processo deixando apenas os números"""
        return re.sub('[^0-9]', '', numero)

    def grau(self, numero):
        """Método que identifica o grau do processo"""
        if numero[-4:] in ['0000', '9100']:
            return self.GRAU_2
        else:
            return self.GRAU_1

    def get_url(self, grau):
        """Método que gera a URL baseada no grau do processo"""
        return settings.EPROC_WSDL_PROCESSOS.format(grau)

    def consultar(self, numero, usuario=settings.EPROC_DEFAULT_USER,
                  senha=settings.EPROC_DEFAULT_PASS):
        """Método que faz a consulta do processo no webservice wsdl"""

        numero = self.numero_puro(numero)
        grau = self.grau(numero)

        self.limpar()

        try:

            client = Client(self.get_url(grau))

            request = client.service.consultarProcesso(
                idConsultante=usuario,
                senhaConsultante=senha,
                numeroProcesso=numero,
                dataReferencia=None,
                movimentos=True,
                documento=True)

            if request:
                self.carregar(request)
                return request.sucesso

        except Exception as e:
            raise Exception(e)

        return False

    def limpar(self):
        """Método que limpa a resposta da consulta"""
        self.resposta = None
        self.sucesso = None
        self.mensagem = None

    def carregar(self, resposta):
        """Método que armazena a resposta da consulta"""
        self.resposta = resposta
        self.sucesso = resposta.sucesso
        self.mensagem = resposta.mensagem
