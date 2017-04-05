# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from mongoengine import (
    Document,
    StringField
)
from config.settings.common import mongo_conn

class Classe(Document):
    codigo = IntField(required=True, unique=True)
    nome = StringField()

    def __unicode__(self):
        return self.nome


class Localidade(Document):
    codigo = IntField(required=True, unique=True)
    nome = StringField()

    def __unicode__(self):
        return self.nome


class OrgaoJulgador(Document):
    codigo = IntField(required=True, unique=True)
    nome = StringField()

    def __unicode__(self):
        return self.nome


class Assunto(Document):
    codigo = IntField(required=True, unique=True)
    nome = StringField()

    def __unicode__(self):
        return self.nome


class ProcessoAssunto(EmbeddedDocument):
    assunto = ReferenceField(Assunto, required=True, unique=True)
    principal = BooleanField(required=True, default=False)

    def __unicode__(self):
        return '{} ({})'.format(self.assunto, self.principal)


class ProcessoVinculado(EmbeddedDocument):

    PROCESSO_VINCULO = (
        ('CX', ''),
        ('CT', ''),
        ('DP', 'Dependente'),
        ('OR', 'Originário'))

    processo = ReferenceField('Processo', required=True)
    vinculo = StringField(max_length=2, choices=PROCESSO_VINCULO)

    def __unicode__(self):
        return '{} ({})'.format(self.processo, self.vinculo)


class ProcessoPolo(EmbeddedDocument):

    POLO_TIPO = (
        ('AD', 'Assistente Simples Desinteressado (amicus curiae)'),
        ('AT', 'Polo Ativo'),
        ('FL', 'Fiscal da Lei Diverso'),
        ('PA', 'Polo Passivo'),
        ('TC', 'Terceiro'),
        ('TJ', 'Testemunha do Juízo'),
        ('VI', 'Vítima'))

    tipo = StringField(max_length=2, choices=POLO_TIPO, required=True, unique=True)
    partes = ListField(EmbeddedDocumentField(ProcessoAssunto))

class ProcessoPoloParte(EmbeddedDocument):
    pessoa = EmbeddedDocumentField('ProcessoPoloPartePessoa')
    advogados = ListField(EmbeddedDocumentField('ProcessoPoloParteAdvogado'))


class ProcessoPoloPartePessoa(EmbeddedDocument):

    PESSOA_TIPO = (
        ('fisica', 'Física'),
        ('juridica', 'Jurídica'),
        ('autoridade', 'Autoridade'),
        ('orgaorepresentacao', 'Orgão de Representação'))

    PESSOA_SEXO = (
        ('M', 'Física'),
        ('F', 'Jurídica'),
        ('D', 'Diverso'))

    tipo = StringField(max_length=2, choices=PESSOA_TIPO)
    documento_principal = StringField()
    nome = StringField()
    nome_genitor = StringField()
    nome_genitora = StringField()
    data_nascimento = DateTimeField()
    data_obito = DateTimeField()
    sexo = StringField(max_length=1, choices=PESSOA_SEXO)
    cidade_natural = StringField()
    estado_natural = StringField(max_length=2)
    nacionalidade = StringField(max_length=2)
    enderecos = ListField(EmbeddedDocumentField('ProcessoPoloPartePessoaEndereco'))


class ProcessoPoloPartePessoaEndereco(EmbeddedDocument):
    cep = StringField(max_length=10)
    logradouro = StringField()
    numero = StringField()
    complemento = StringField()
    bairro = StringField()
    cidade = StringField()
    estado = StringField(max_length=2)
    pais = StringField()


class ProcessoPoloParteAdvogado(EmbeddedDocument):

    ADVOGADO_TIPO = (
        ('A', ''),
        ('E', ''),
        ('M', ''),
        ('D', ''),
        ('P', ''))

    nome = StringField()
    documento_principal = StringField()
    identidade_principal = StringField()
    tipo_representante = StringField(max_length=1, choices=ADVOGADO_TIPO)


class ProcessoEvento(EmbeddedDocument):

    EVENTO_NIVEL_SIGILO = (
        (0, 'Público'),
        (1, 'Segredo de Justiça'),
        (2, 'Sigiloso'))

    evento = IntField(required=True, unique=True)
    data_protocolo = DateTimeField()
    nivel_sigilo = IntField(choices=EVENTO_NIVEL_SIGILO)
    tipo_local = StringField()
    tipo_nacional = StringField()
    usuario = StringField()
    documentos = ListField(EmbeddedDocumentField('ProcessoDocumento'))


class ProcessoDocumento(EmbeddedDocument):
    documento = StringField(required=True, unique=True)
    tipo = StringField()
    nome = StringField()
    mimetype = StringField()


class Processo(Document):

    PROCESSO_GRAU = (
        (1, '1º Grau'),
        (2, '2º Grau'))

    PROCESSO_NIVEL_SIGILO = (
        (0, 'Público'),
        (1, 'Segredo de Justiça'),
        (2, 'Sigiloso'))

    numero = StringField(max_length=20, required=True, unique=True)
    chave = StringField(max_length=50)
    grau = IntField(choices=PROCESSO_GRAU)
    classe = ReferenceField(Classe)
    localidade = ReferenceField(Localidade)
    orgao_julgador = ReferenceField(OrgaoJulgador)
    nivel_sigilo = IntField(choices=PROCESSO_NIVEL_SIGILO)
    valor_causa = DecimalField(precision=2)
    assuntos = ListField(EmbeddedDocumentField(ProcessoAssunto))
    vinculados = ListField(EmbeddedDocumentField(ProcessoVinculado))
    polos = ListField(EmbeddedDocumentField(ProcessoPolo))
    eventos = ListField(EmbeddedDocumentField(ProcessoEvento))
    data_ultimo_movimento = DateTimeField()
    data_ultima_atualizacao = DateTimeField()
    atualizado = BooleanField(default=False)

    def __unicode__(self):
        return self.numero

