# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals


import datetime
from decimal import Decimal
from mixer.backend.mongoengine import Mixer
from mongoengine import *

from procapi.processo.models import (
    Processo,
    ProcessoAssunto,
    ProcessoClasse,
    ProcessoLocalidade,
    ProcessoOrgaoJulgador,
    ProcessoVinculado
)

class TestProcesso():
    mixer = Mixer(commit=False)
    processo_obj = mixer.blend(Processo)
    processo_attr = [
        'id',
        'numero',
        'chave',
        'grau',
        'classe',
        'localidade',
        'orgao_julgador',
        'nivel_sigilo',
        'valor_causa',
        'assuntos',
        'vinculados',
        'data_ultimo_movimento',
        'data_ultima_atualizacao',
        'atualizado'
    ]

    processo_classe =  mixer.blend(ProcessoClasse, codigo="1212",
        nome="Inquerito Policial")

    processo_localidade = mixer.blend(ProcessoLocalidade, codigo="2720",
        nome="Palmas")

    processo_orgao_julgador = mixer.blend(ProcessoOrgaoJulgador,
        codigo="TOPAL2CIV", nome="2ª Vara Civel de Palmas")

    assunto = mixer.blend(ProcessoAssunto, principal=True, codigo="1681",
        nome="Periculosidade")

    vinculado = mixer.blend(ProcessoVinculado, vinculo="DP",
        numero="0000015320178272721")

    processo = mixer.blend(Processo, numero='00000015320178272720', grau=1,
        chave='000000000000000000000000', nivel_sigilo=2, atualizado=False,
        data_ultimo_movimento=datetime.datetime(2017,1,1,0,0,1,9999),
        data_ultima_atualizacao=datetime.datetime(2017,1,1,0,0,1,9999),
        valor_causa=Decimal('1270.12'))

    processo.classe = processo_classe
    processo.localidade = processo_localidade
    processo.orgao_julgador = processo_orgao_julgador
    processo.assuntos.append(assunto)
    processo.vinculados.append(vinculado)

    def test_processo_quantidade_atributos(self):
        assert self.processo_obj.__len__() == 14

    def test_processo_atributos_existentes(self):
        for att in self.processo_attr:
            assert hasattr(Processo(), att)

    def test_processo_atributos_validos(self):
        assert self.processo.numero != None
        assert isinstance(self.processo.numero, unicode)

    def test_processo_representacao(self):
        assert str(self.processo) == self.processo.numero

    def test_processo_chave(self):
        assert self.processo.chave
        assert self.processo.chave.__len__() <= 50

    def test_processo_grau(self):
        assert self.processo.grau in [1,2]

    def test_processo_classe(self):
        assert self.processo.classe.nome == self.processo_classe.nome

    def test_processo_localidade_cidade(self):
        assert self.processo.localidade.nome == 'Palmas'

    def test_processo_orgao_julgador_codigo(self):
        assert self.processo.orgao_julgador.codigo == 'TOPAL2CIV'

    def test_processo_nivel_sigilo(self):
        assert self.processo.nivel_sigilo in [0,1,2]

    def test_processo_valor_causa(self):
        assert self.processo.valor_causa == Decimal('1270.12')

    def test_processo_assuntos(self):
        assert self.processo.assuntos.count() == 1
        assert self.processo.assuntos.first().codigo == '1681'

    def test_processo_vinculados(self):
        assert self.processo.vinculados.count() == 1
        assert self.processo.vinculados.first().numero == '0000015320178272721'

    def test_processo_data_ultimo_movimento(self):
        assert self.processo.data_ultimo_movimento

    def test_processo_data_ultima_atualizacao(self):
        assert self.processo.data_ultima_atualizacao

    def test_processo_atualizado(self):
        assert self.processo.atualizado == False

    def test_processo_partes(self):
        assert self.processo.partes.__len__() == 0

    def test_processo_eventos(self):
        assert self.processo.eventos.__len__() == 0


class TestProcessoClasse():
    mixer = Mixer(commit=False)
    classe_obj = mixer.blend(ProcessoClasse)
    classe_attr = [
        'codigo',
        'nome'
    ]
    classe =  mixer.blend(ProcessoClasse, codigo="1212", nome="Inquerito Policial")

    def test_classe_quantidade_atributos(self):
        assert self.classe_obj.__len__() == 2

    def test_classe_atributos_existentes(self):
        for att in self.classe_attr:
            assert hasattr(ProcessoClasse(), att)

    def test_classe_atributos_validos(self):
        assert self.classe.codigo != None
        assert self.classe.nome != None

    def test_classe_representacao(self):
        assert str(self.classe) == self.classe.nome


class TestProcessoLocalidade():
    mixer = Mixer(commit=False)
    localidade_obj = mixer.blend(ProcessoLocalidade)
    localidade_attr = [
        'codigo',
        'nome'
    ]
    localidade = mixer.blend(ProcessoLocalidade, codigo="2720", nome="Palmas")

    def test_localidade_quantidade_atributos(self):
        assert self.localidade_obj.__len__() == 2

    def test_localidade_atributos_existentes(self):
        for att in self.localidade_attr:
            assert hasattr(ProcessoLocalidade(), att)

    def test_localidade_representacao(self):
        assert str(self.localidade) == self.localidade.nome

    def test_localidade_atributos_validos(self):
        assert self.localidade.codigo != None
        assert self.localidade.nome != None


class TestProcessoOrgaoJulgador():
    mixer = Mixer(commit=False)
    orgao_julgador_obj = mixer.blend(ProcessoOrgaoJulgador)
    orgao_julgador_attr = [
        'codigo',
        'nome'
    ]
    orgao_julgador = mixer.blend(ProcessoOrgaoJulgador, codigo="TOPAL2CIV",
        nome="2a Vara Civel de Palmas")

    def test_orgao_quantidade_atributos(self):
        assert self.orgao_julgador_obj.__len__() == 2

    def test_orgao_atributos_existentes(self):
        for att in self.orgao_julgador_attr:
            assert hasattr(ProcessoOrgaoJulgador(), att)

    def test_orgao_representacao(self):
        assert str(self.orgao_julgador) == self.orgao_julgador.nome

    def test_orgao_atributos_validos(self):
        assert self.orgao_julgador.codigo != None
        assert self.orgao_julgador.nome != None


class TestProcessoAssunto():
    mixer = Mixer(commit=False)
    assunto_obj = mixer.blend(ProcessoAssunto)
    assunto_attr = [
        'codigo',
        'nome'
    ]
    assunto = mixer.blend(ProcessoAssunto, principal=True, codigo="1681",
        nome="Periculosidade")

    def test_assunto_quantidade_atributos(self):
        assert self.assunto_obj.__len__() == 3

    def test_assunto_atributos_existentes(self):
        for att in self.assunto_attr:
            assert hasattr(ProcessoAssunto(), att)

    def test_assunto_representacaoo(self):
        assert str(self.assunto) == '{} ({})'.format(
            self.assunto.nome, self.assunto.principal)

    def test_assunto_atributos_validos(self):
        assert self.assunto.codigo != None
        assert self.assunto.nome != None

    def test_assunto_principal(self):
        assert self.assunto.principal


class TestProcessoVinculado():
    mixer = Mixer(commit=False)
    processo_vinculado_obj = mixer.blend(ProcessoVinculado)
    processo_vinculado_obj_attr = [
        'numero',
        'vinculo'
    ]
    processo_vinculado = mixer.blend(ProcessoVinculado, vinculo="DP",
        numero="00000015320178272721")

    def test_vinculado_quantidade_atributos(self):
        assert self.processo_vinculado_obj.__len__() == 2

    def test_processo_caracteres_numero(self):
        assert self.processo_vinculado.numero
        assert self.processo_vinculado.numero.__len__() <= 20

    def test_vinculado_atributos_existentes(self):
        for att in self.processo_vinculado_obj:
            assert hasattr(ProcessoVinculado(), att)

    def test_vinculado_atributos_validos(self):
        assert self.processo_vinculado.numero
        assert self.processo_vinculado.vinculo

    def test_vinculado_representacao(self):
        assert str(self.processo_vinculado) == '{} ({})'.format(self.processo_vinculado.numero, self.processo_vinculado.vinculo)

    def test_vinculado_vinculo_existente(self):
        assert self.processo_vinculado.vinculo in ['CX','CT','DP','OR']
