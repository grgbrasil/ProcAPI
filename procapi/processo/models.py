# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.core.urlresolvers import reverse
from mongoengine import (
    BooleanField,
    DecimalField,
    DateTimeField,
    Document,
    DynamicDocument,
    EmbeddedDocument,
    EmbeddedDocumentField,
    EmbeddedDocumentListField,
    IntField,
    ListField,
    ReferenceField,
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
    codigo = StringField(required=True, unique=True)
    nome = StringField()

    def __unicode__(self):
        return self.nome


class Assunto(Document):
    codigo = IntField(required=True, unique=True)
    nome = StringField()

    def __unicode__(self):
        return self.nome

class ProcessoClasse(EmbeddedDocument):
    codigo = IntField(required=True)
    nome = StringField()


class ProcessoLocalidade(EmbeddedDocument):
    codigo = IntField(required=True)
    nome = StringField()


class ProcessoOrgaoJulgador(EmbeddedDocument):
    codigo = StringField(required=True)
    nome = StringField()


class ProcessoAssunto(EmbeddedDocument):
    principal = BooleanField(required=True, default=False)
    codigo = IntField(required=True)
    nome = StringField()

    def __unicode__(self):
        return '{} ({})'.format(self.nome, self.principal)


class ProcessoVinculado(EmbeddedDocument):
    PROCESSO_VINCULO = (
        ('CX', ''),
        ('CT', ''),
        ('DP', 'Dependente'),
        ('OR', 'Originário'))

    numero = StringField(max_length=20, required=True)
    vinculo = StringField(max_length=2, choices=PROCESSO_VINCULO, required=True)

    def __unicode__(self):
        return '{} ({})'.format(self.numero, self.vinculo)


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
    classe = EmbeddedDocumentField('ProcessoClasse')
    localidade = EmbeddedDocumentField('ProcessoLocalidade')
    orgao_julgador = EmbeddedDocumentField('ProcessoOrgaoJulgador')
    nivel_sigilo = IntField(choices=PROCESSO_NIVEL_SIGILO)
    valor_causa = DecimalField(precision=2)
    assuntos = EmbeddedDocumentListField('ProcessoAssunto')
    vinculados = EmbeddedDocumentListField('ProcessoVinculado')
    # polos = ReferenceField('ListaPolos')
    data_ultimo_movimento = DateTimeField()
    data_ultima_atualizacao = DateTimeField()
    atualizado = BooleanField(default=False)

    def __unicode__(self):
        return self.numero

    @property
    def eventos(self):
        return Evento.objects.filter(processo=self)

    @property
    def partes(self):
        return Parte.objects.filter(processo=self)


class ProcessoBruto(DynamicDocument):
    processo = ReferenceField('Processo', required=True, unique=True)


class PartePessoa(EmbeddedDocument):
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
    enderecos = EmbeddedDocumentListField('PartePessoaEndereco')


class PartePessoaEndereco(EmbeddedDocument):
    cep = StringField(max_length=10)
    logradouro = StringField()
    numero = StringField()
    complemento = StringField()
    bairro = StringField()
    cidade = StringField()
    estado = StringField(max_length=2)
    pais = StringField()


class ParteAdvogado(EmbeddedDocument):
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


class Parte(Document):
    POLO_TIPO = (
        ('AD', 'Assistente Simples Desinteressado (amicus curiae)'),
        ('AT', 'Polo Ativo'),
        ('FL', 'Fiscal da Lei Diverso'),
        ('PA', 'Polo Passivo'),
        ('TC', 'Terceiro'),
        ('TJ', 'Testemunha do Juízo'),
        ('VI', 'Vítima'))

    processo = ReferenceField('Processo', dbref=True)
    tipo = StringField(
        max_length=2, choices=POLO_TIPO, required=True)
    pessoa = EmbeddedDocumentField('PartePessoa')
    advogados = EmbeddedDocumentListField('ParteAdvogado')


class Evento(Document):
    NIVEL_SIGILO = (
        (0, 'Público'),
        (1, 'Segredo de Justiça'),
        (2, 'Sigiloso'))

    processo = ReferenceField('Processo', dbref=True)
    numero = IntField(required=True)
    data_protocolo = DateTimeField()
    nivel_sigilo = IntField(choices=NIVEL_SIGILO)
    tipo_local = StringField()
    tipo_nacional = StringField()
    usuario = StringField()
    documentos = EmbeddedDocumentListField('EventoDocumento')


class EventoDocumento(EmbeddedDocument):
    documento = StringField(required=True)
    tipo = StringField()
    nome = StringField()
    mimetype = StringField()
