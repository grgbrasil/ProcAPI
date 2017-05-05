import json
import logging
import math
import re
import xml.etree.ElementTree as ET

from suds.client import Client
from suds.sudsobject import asdict
from django.conf import settings

loggerWS = logging.getLogger('eproc')


class ConsultaEProc(object):
    """Consulta Processual E-Proc"""

    GRAU_1 = 1
    GRAU_2 = 2

    numero = None
    resposta = None
    sucesso = None
    mensagem = None

    def numero_puro(self, numero):
        """Método que formata o numero do processo deixando apenas os números"""
        return re.sub('[^0-9]', '', numero)

    def grau(self, numero):
        """Método que identifica o grau do processo"""
        if numero[-2:] == '00':
            return self.GRAU_2
        else:
            return self.GRAU_1

    def get_url(self, grau):
        """Método que gera a URL baseada no grau do processo"""
        return settings.EPROC_WSDL_PROCESSOS.format(grau)

    def consultar(self, numero, usuario=settings.EPROC_DEFAULT_USER,
                  senha=settings.EPROC_DEFAULT_PASS):
        """Método que faz a consulta do processo no webservice wsdl"""

        self.numero = self.numero_puro(numero)
        grau = self.grau(numero)

        self.limpar()

        try:

            client = Client(self.get_url(grau))

            request = client.service.consultarProcesso(
                idConsultante=usuario,
                senhaConsultante=senha,
                numeroProcesso=self.numero,
                dataReferencia=None,
                movimentos=True,
                documento=True)

            if request:
                loggerWS.info('service.consultarProcesso',
                              extra={'params': {
                                  'url': self.get_url(grau),
                                  'idConsultante': usuario,
                                  'numeroProcesso': self.numero,
                                  'dataReferencia': None,
                                  'movimentos': True,
                                  'documento': True
                              }})

                self.carregar(request)
                # Rodar task de registro de acesso com sucesso...
                return request.sucesso

        except Exception as ex:
            loggerWS.critical(ex,
                              extra={'params': {
                                  'url': self.get_url(grau),
                                  'idConsultante': usuario,
                                  'numeroProcesso': self.numero,
                                  'dataReferencia': None,
                                  'movimentos': True,
                                  'documento': True
                              }})

        # Rodar task de registro de acesso com erro...
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

    def __suds_to_dict(self, data):
        """Converte sudsobject para dict"""
        out = {}
        for key, value in list(asdict(data).items()):
            if hasattr(value, '__keylist__'):
                out[key] = self.__suds_to_dict(value)
            elif isinstance(value, list):
                out[key] = []
                for item in value:
                    if hasattr(item, '__keylist__'):
                        out[key].append(self.__suds_to_dict(item))
                    else:
                        out[key].append(item)
            else:
                out[key] = value
        return out

    def __suds_to_json(self, data):
        """Converte sudsobject para json"""
        return json.dumps(self.__suds_to_dict(data))

    def resposta_to_dict(self):
        """Converte resposta do webservice wsdl para o formato dict"""
        if self.resposta:
            return self.__suds_to_dict(self.resposta.processo)

    def resposta_to_json(self):
        """Converte resposta do webservice wsdl para o formato json"""
        if self.resposta:
            return self.__suds_to_json(self.resposta.processo)


class ConsultaEProcMovimentados(object):
    """Consulta Processos Movimentos no E-Proc"""

    grau = None
    data_inicial = None
    data_final = None
    max_registros = None
    total_registros = None
    total_paginas = None
    pagina = None

    def __init__(self, grau, data_inicial, data_final, max_registros):
        """Inicialização da instância da classe"""
        self.grau = grau
        self.data_inicial = data_inicial
        self.data_final = data_final
        self.max_registros = max_registros

    def get_url(self, grau):
        """Gera a URL baseada no grau do processo"""
        return settings.EPROC_WSDL_SERVICOS.format(grau)

    def consultar(self, pagina=None):
        """Consulta processos da página informada"""

        try:

            client = Client(self.get_url(self.grau), headers={'User-Agent': 'DPE-TO'})

            resposta = client.service.consultarProcessosAlteracaoPeriodo(
                dataHoraInicio=self.data_inicial.strftime("%Y-%m-%d %H:%M:%S"),
                dataHoraFim=self.data_final.strftime("%Y-%m-%d %H:%M:%S"),
                entidade='DPU',
                paginate=0 if pagina is None else pagina,
                numMaxRegistrosRetorno=self.max_registros,
                numPaginaAtual=pagina)

            loggerWS.info('service.consultarProcessosAlteracaoPeriodo',
                          extra={'params': {
                              'url': self.get_url(self.grau),
                              'dataHoraInicio': self.data_inicial.strftime("%Y-%m-%d %H:%M:%S"),
                              'dataHoraFim': self.data_final.strftime("%Y-%m-%d %H:%M:%S"),
                              'entidade': 'DPU',
                              'paginate': 1,
                              'numMaxRegistrosRetorno': self.max_registros,
                              'numPaginaAtual': pagina
                          }})

            root_grau = ET.fromstring(resposta)
            lista_processos = []

            for child in root_grau:
                if child.tag == 'total':
                    self.total_registros = int(child.text)
                elif child.tag == 'numProcesso':
                    lista_processos.append(child.text)

            if pagina == 0:
                self.calcular_total_paginas()

            return lista_processos

        except Exception as ex:
            loggerWS.critical('service.consultarProcessosAlteracaoPeriodo',
                              extra={'params': {
                                  'url': self.get_url(self.grau),
                                  'dataHoraInicio': self.data_inicial.strftime("%Y-%m-%d %H:%M:%S"),
                                  'dataHoraFim': self.data_final.strftime("%Y-%m-%d %H:%M:%S"),
                                  'entidade': 'DPU',
                                  'paginate': 1,
                                  'numMaxRegistrosRetorno': self.max_registros,
                                  'numPaginaAtual': pagina
                              }})

        return None

    def calcular_total_paginas(self):
        """Calcula total de páginas baseado no total de registros"""
        self.total_paginas = int(math.ceil(float(self.total_registros) / self.max_registros))
