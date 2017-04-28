# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
from celery import Celery, shared_task
from datetime import datetime, timedelta

from procapi.utils.services import ConsultaEProcMovimentados, ConsultaEProc
from procapi.processo.models import Processo

app = Celery('procapi_tasks')
app.config_from_object('django.conf:settings', namespace='CELERY')

from config.settings.common import mongo_conn

logger = logging.getLogger(__name__)


@shared_task
def consultar_processos_movimentados_periodo(grau, periodo, execucao_inicial, execucao_final, max_registros=None, pagina=None):
    """Baixa o número dos processos movimentos em um intervalo de tempo"""

    data  = datetime.now()
    data = datetime(data.year, data.month, data.day, data.hour, data.minute)
    hora = data.time()

    execucao_inicial = datetime.strptime(execucao_inicial,'%H:%M').time()
    execucao_final = datetime.strptime(execucao_final,'%H:%M').time()

    data_final = data
    data_inicial = data_final-timedelta(minutes=periodo)

    if execucao_inicial < execucao_final:
        if not (hora >= execucao_inicial and hora <= execucao_final):
            return "Task fora do período {} - {}".format(execucao_inicial,execucao_final)
    else:
        if not(hora >= execucao_inicial or hora <= execucao_final):
            return "Task fora do período {} - {}".format(execucao_inicial,execucao_final)

    return consultar_processos_movimentados(
        grau=grau,
        data_inicial=data_inicial,
        data_final=data_final,
        max_registros=max_registros,
        pagina=pagina
    )


@shared_task
def consultar_processos_movimentados(grau, data_inicial, data_final, max_registros=None, pagina=None):
    """Baixa o número dos processos movimentos em um intervalo de datas"""

    if not isinstance(data_inicial, datetime) and not isinstance(data_final, datetime):
        data_inicial = datetime.strptime(data_inicial, "%Y-%m-%d %H:%M:%S")
        data_final = datetime.strptime(data_final, "%Y-%m-%d %H:%M:%S")

    consulta = ConsultaEProcMovimentados(
        grau=grau,
        data_inicial=data_inicial,
        data_final=data_final,
        max_registros=max_registros)

    resposta = consulta.consultar(pagina=pagina)

    if resposta:
        for processo in resposta:
            criar_processo_movimentado.delay(numero=processo)
        return True
    else:
        #Não conseguiu consultar. Repetir metodo?
        return False


@shared_task
def criar_processo_movimentado(numero):
    """Cria processo movimentado ou marca como desatualizado"""
    processo = Processo.objects.filter(numero=numero).first()
    if processo:
        processo.atualizado = False
        processo.save()
        return {"numero": processo.numero, "novo": False}
    else:
        processo = Processo.objects.create(numero=numero, atualizado=False)
    return {"numero": processo.numero, "novo": True}


@shared_task
def atualizar_processos_desatualizados():
    """Recupera lista de processos desatualizados para atualização individual"""
    processos = Processo.objects.filter(atualizado=False).values_list('numero')
    print('{} processos serão atualizados'.format(len(processos)))
    for processo in processos:
        atualizar_processo_desatualizado(processo)


@shared_task
def atualizar_processo_desatualizado(numero):
    """Atualiza informações de um processo consultando serviço externo
    1 - verifica se processo existe no banco de dados
    2 - se não existe, cria processo desatualizado
    3 - consulta serviço externo
    4 - registra consulta na tabela de consultas
    5 - se resposta sucesso, cria processo bruto
    6 - se resposta sucesso, chama 'extrair_dados_processo_bruto'
    """

    processo = Processo.objects.filter(numero=numero).first()

    consulta = ConsultaEProc()

    if consulta.consultar(numero):

        eproc = ProcessoBruto.objects.filter(processo=processo).first()

        if eproc:
            eproc.__dict__.update(consulta.resposta_to_dict())
            eproc.save()
        else:
            eproc = ProcessoBruto.objects.create(processo=processo, **consulta.resposta_to_dict())

        extrair_dados_processo_bruto(numero)

        print('Processo {} atualizado'.format(numero))

    else:

        print('Erro ao atualizar processo {}: {}'.format(numero,
            consulta.mensagem))


@shared_task
def extrair_dados_processo_bruto(numero):
    """Atualizar dados do processo apartir da extração dos dados brutos armazenados"""
    processo = Processo.objects(numero=numero).first()
    eproc = ProcessoBruto.objects(processo=processo).first()
    extrair_cabecalho_processo_bruto(eproc)
    extrair_eventos_processo_bruto(eproc)
    extrair_partes_processo_bruto(eproc)


@shared_task
def extrair_cabecalho_processo_bruto(eproc):
    """Atualizar dados cabecalho do processo apartir da extração dos dados brutos armazenados"""
    processo = eproc.processo

    # Classe
    classe = Classe.objects.filter(codigo=eproc.dadosBasicos.get('_classeProcessual')).first()

    if classe:
        processo.classe = ProcessoClasse(codigo=classe.codigo, nome=classe.nome)
    else:
        processo.classe = None

    # Localidade
    localidade = Localidade.objects.filter(codigo=eproc.dadosBasicos.get('_codigoLocalidade')).first()

    if localidade:
        processo.localidade = ProcessoLocalidade(codigo=localidade.codigo, nome=localidade.nome)
    else:
        processo.localidade = None

    # Orgão
    orgao = OrgaoJulgador.objects.filter(codigo=eproc.dadosBasicos.get('_codigoOrgaoJulgador')).first()

    if orgao:
        processo.orgao_julgador = ProcessoOrgaoJulgador(codigo=orgao.codigo, nome=orgao.nome)
    else:
        processo.orgao_julgador = None

    # Assuntos
    processo.assuntos = None
    if 'assunto' in eproc.dadosBasicos:
        for item in eproc.dadosBasicos['assunto']:
            assunto = Assunto.objects.filter(codigo=item.get('codigoNacional')).first()
            if assunto:
                processo.assuntos.append(
                    ProcessoAssunto(
                        codigo=assunto.codigo,
                        nome=assunto.nome
                    )
                )

    # Vinculados
    processo.vinculados = None
    if 'processoVinculado' in eproc.dadosBasicos:
        processo.vinculados.exclude()
        for item in eproc.dadosBasicos.get('processoVinculado'):
            processo.vinculados.append(
                ProcessoVinculado(
                    numero=item.get('_numeroProcesso'),
                    vinculo=item.get('_vinculo')
                )
            )

    # Outros
    # processo.grau = consulta.grau(processo.numero)
    processo.nivel_sigilo = eproc.dadosBasicos['_nivelSigilo']
    processo.valor_causa = eproc.dadosBasicos['valorCausa']
    processo.data_ultimo_movimento = None
    processo.data_ultima_atualizacao = datetime.now()
    processo.atualizado = True

    processo.save()

    print('Cabecalho do processo {} extraído com sucesso!'.format(processo.numero))


@shared_task
def extrair_eventos_processo_bruto(eproc):
    """Atualizar eventos do processo apartir da extração dos dados brutos armazenados"""
    processo = eproc.processo

    documentos = {}
    for item in eproc.documento:
        documentos[item.get('_idDocumento')] = item

    tipos_documentos = TipoDocumento.objects.filter(grau=processo.grau).values_list('codigo', 'nome')
    tipos_documentos = dict((x,y) for x, y in tipos_documentos)

    for item in eproc.movimento:

        if not Evento.objects.filter(processo=processo, numero=item.get('_identificadorMovimento')).count():

            evento = Evento(
                processo=processo,
                numero=item.get('_identificadorMovimento'),
                data_protocolo=datetime.strptime(item.get('_dataHora'), '%Y%m%d%H%M%S'),
                nivel_sigilo = item.get('_nivelSigilo'),
                tipo_local = item.get('_identificadorMovimentoLocal'),
                usuario = item.get('_identificadorUsuarioMovimentacao'),
                descricao = item.get('movimentoLocal')
            )

            evento.documentos = None

            if 'idDocumentoVinculado' in item:
                for documento in item['idDocumentoVinculado']:
                    documento = documentos[documento]
                    documento = EventoDocumento(
                        documento=documento.get('_idDocumento'),
                        tipo=documento.get('_tipoDocumento'),
                        nome=tipos_documentos[int(documento.get('_tipoDocumento'))] if int(documento.get('_tipoDocumento')) in tipos_documentos else None,
                        mimetype=documento.get('_mimetype')
                    )
                    evento.documentos.append(documento)
            if usuario[:2].upper() == 'DP' and range(0,9) in usuario[3]:
                evento.defensoria = True
            evento.save()

    print('Eventos do processo {} extraídos com sucesso!'.format(processo.numero))


@shared_task
def extrair_partes_processo_bruto(eproc):
    """Atualizar partes do processo apartir da extração dos dados brutos armazenados"""
    processo = eproc.processo

    Parte.objects.filter(processo=processo).delete()

    for polo in eproc.dadosBasicos['polo']:

        for item in polo['parte']:

            parte = Parte(
                processo=processo,
                tipo=polo.get('_polo'),
            )

            pessoa = item.get('pessoa')

            parte.pessoa = PartePessoa(
                tipo=pessoa.get('_tipoPessoa'),
                documento_principal=pessoa.get('_numeroDocumentoPrincipal'),
                nome=pessoa.get('_nome'),
                nome_genitor=pessoa.get('_nomeGenitor'),
                nome_genitora=pessoa.get('_nomeGenitora'),
                data_nascimento=datetime.strptime(pessoa.get('_dataNascimento'), '%Y%m%d') if pessoa.get('_dataNascimento') else None,
                data_obito=datetime.strptime(pessoa.get('_dataObito'), '%Y%m%d') if pessoa.get('_dataObito') else None,
                sexo=pessoa.get('_sexo') if pessoa.get('_sexo') else None,
                cidade_natural=pessoa.get('_cidadeNatural'),
                estado_natural=pessoa.get('_estadoNatural'),
                nacionalidade=pessoa.get('_nacionalidade'),
            )

            if 'endereco' in pessoa:
                for endereco in pessoa['endereco']:
                    parte.pessoa.enderecos.append(
                        PartePessoaEndereco(
                            cep=endereco.get('_cep'),
                            logradouro=endereco.get('logradouro'),
                            numero=endereco.get('numero'),
                            complemento=endereco.get('complemento'),
                            bairro=endereco.get('bairro'),
                            cidade=endereco.get('cidade'),
                            estado=endereco.get('estado'),
                            pais=endereco.get('pais')
                        )
                    )

            if 'advogado' in item:
                for advogado in item['advogado']:
                    parte.advogados.append(
                        ParteAdvogado(
                            nome=advogado.get('_nome'),
                            documento_principal=advogado.get('_numeroDocumentoPrincipal'),
                            identidade_principal=advogado.get('_identidadePrincipal'),
                            tipo_representante=advogado.get('_tipoRepresentante')
                        )
                    )

            parte.save()

    print('Partes do processo {} extraídas com sucesso!'.format(processo.numero))
