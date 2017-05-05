# -*- coding: utf-8 -*-


from django.core.urlresolvers import reverse
from django.utils.encoding import python_2_unicode_compatible
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


@python_2_unicode_compatible
class Classe(Document):
    codigo = IntField(required=True, unique=True)
    nome = StringField()

    def __str__(self):
        return self.nome


@python_2_unicode_compatible
class Localidade(Document):
    codigo = IntField(required=True, unique=True)
    nome = StringField()

    def __str__(self):
        return self.nome


@python_2_unicode_compatible
class OrgaoJulgador(Document):
    codigo = StringField(required=True, unique=True)
    nome = StringField()

    def __str__(self):
        return self.nome


@python_2_unicode_compatible
class Assunto(Document):
    codigo = IntField(required=True, unique=True)
    nome = StringField()

    def __str__(self):
        return self.nome


@python_2_unicode_compatible
class ProcessoClasse(EmbeddedDocument):
    codigo = IntField(required=True)
    nome = StringField()

    def __str__(self):
        return '{}'.format(self.nome)


@python_2_unicode_compatible
class ProcessoLocalidade(EmbeddedDocument):
    codigo = IntField(required=True)
    nome = StringField()

    def __str__(self):
        return self.nome


@python_2_unicode_compatible
class ProcessoOrgaoJulgador(EmbeddedDocument):
    codigo = StringField(required=True)
    nome = StringField()

    def __str__(self):
        return self.nome


@python_2_unicode_compatible
class ProcessoAssunto(EmbeddedDocument):
    principal = BooleanField(required=True, default=False)
    codigo = IntField(required=True)
    nome = StringField()

    def __str__(self):
        return '{} ({})'.format(self.nome, self.principal)


@python_2_unicode_compatible
class ProcessoVinculado(EmbeddedDocument):
    PROCESSO_VINCULO = (
        ('CX', ''),
        ('CT', ''),
        ('DP', 'Dependente'),
        ('OR', 'Originário'))

    numero = StringField(max_length=20, required=True)
    vinculo = StringField(max_length=2, choices=PROCESSO_VINCULO,
        required=True)

    def __str__(self):
        return '{} ({})'.format(self.numero, self.vinculo)


@python_2_unicode_compatible
class Processo(Document):
    GRAU_1 = 1
    GRAU_2 = 2

    PROCESSO_GRAU = (
        (GRAU_1, '1º Grau'),
        (GRAU_2, '2º Grau'))
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
    data_ultimo_movimento = DateTimeField()
    data_ultima_atualizacao = DateTimeField()
    atualizado = BooleanField(default=False)
    atualizando = BooleanField(default=False)

    def __str__(self):
        return self.numero

    def save(self, *args, **kwargs):
        self.grau = self._identificar_grau()
        return super(Processo, self).save(*args, **kwargs)

    def _identificar_grau(self):
        """Método que identifica o grau do processo"""
        if str(self.numero)[-4:] in ['0000', '9100']:
            grau = self.GRAU_2
        else:
            grau = self.GRAU_1

        return grau

    @property
    def eventos(self):
        return Evento.objects.filter(processo=self)

    @property
    def partes(self):
        return Parte.objects.filter(processo=self)


@python_2_unicode_compatible
class ProcessoBruto(DynamicDocument):
    processo = ReferenceField('Processo', required=True, unique=True)

    def __str__(self):
        return self.processo


@python_2_unicode_compatible
class PartePessoa(EmbeddedDocument):
    PESSOA_TIPO = (
        ('fisica', 'Física'),
        ('juridica', 'Jurídica'),
        ('autoridade', 'Autoridade'),
        ('orgaorepresentacao', 'Orgão de Representação'))
    PESSOA_SEXO = (
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('D', 'Diverso'))

    tipo = StringField(choices=PESSOA_TIPO)
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

    def __str__(self):
        return '{}-{}'.format(self.nome, self.documento_principal)


@python_2_unicode_compatible
class PartePessoaEndereco(EmbeddedDocument):
    cep = StringField(max_length=10)
    logradouro = StringField()
    numero = StringField()
    complemento = StringField()
    bairro = StringField()
    cidade = StringField()
    estado = StringField(max_length=2)
    pais = StringField()

    def __str__(self):
        return ''


@python_2_unicode_compatible
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

    def __str__(self):
        return '{}-{}:{}'.format(self.tipo_representante, self.nome,
            self.identidade_principal)


@python_2_unicode_compatible
class Parte(Document):
    POLO_TIPO = (
        ('', 'Outros'),
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

    def __str__(self):
        return '{}:{}-{}'.format(self.processo, self.tipo, self.pessoa)


@python_2_unicode_compatible
class Evento(Document):
    NIVEL_SIGILO = (
        (0, 'Público'),
        (1, 'Segredo de Justiça'),
        (2, 'Sigiloso'))

    processo = ReferenceField('Processo', dbref=True)
    numero = IntField(required=True)
    data_protocolo = DateTimeField()
    descricao = StringField()
    nivel_sigilo = IntField(choices=NIVEL_SIGILO)
    tipo_local = StringField()
    tipo_nacional = StringField()
    usuario = StringField()
    defensoria = BooleanField(default=False)
    documentos = EmbeddedDocumentListField('EventoDocumento')

    def __str__(self):
        return 'n°{} {}-{}'.format(self.numero, self.processo, self.usuario)


@python_2_unicode_compatible
class EventoDocumento(EmbeddedDocument):
    documento = StringField(required=True)
    tipo = StringField()
    nome = StringField()
    mimetype = StringField()

    def __str__(self):
        return '{}-{}.{}'.format(self.tipo, self.nome, self.mimetype)


@python_2_unicode_compatible
class TipoDocumento(Document):
    codigo = IntField(required=True, unique=True, unique_with='grau')
    grau = IntField(choices=Processo.PROCESSO_GRAU, required=True)
    nome = StringField()

    def __str__(self):
        return '{}-{}-{}'.format(self.grau, self.nome, self.codigo)
