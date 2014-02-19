#-*- coding: utf-8 -*-
from gluon import URL,XML,I,current,redirect
from custon_helper import AUTORIZED_MENU
from myutils import date2str
from atividade_utils import atividade_inicio,atividade_termino,num_inscritos_

from datetime import datetime


## ordem_inscricao - insc_number

__all__ = ['atividade_menu','ordem_inscricao','frequencia_participacao','certifica_inscrito','pessoa_get_certificados',
           'num_presenca','listas_feitas','periodos_shortcut','atividade_inicio','atividade_termino',
           'data_limite_avaliacao',
           'atividade_areas_conhecimento','data_limite_submissao','versao_dataRes','versao_editar','versao_status',
           'versao_prazo','artigo_avaliacao_liberada']


T = current.T
def insc_online_subativs_(db,atividade):
    """Se as subatividades liberam inscrição on_line"""
    if  atividade.tipo=="ev":
        subatividade = db.atividade_subatividades
        return bool(db(((subatividade.mestra_id==atividade.id) & (subatividade.subatividade_id==db.atividade.id)) |\
                       ((subatividade.subatividade_id==atividade.id) & (subatividade.mestra_id==db.atividade.id)) &\
                       db.atividade.insc_online==True).select(db.atividade.id) )
                    

def em_periodo_confirmacao(db,atividade):
    if atividade_termino(db,atividade):
        return
    inicio = atividade.inicio_confirmacao or date.today()
    termino = atividade.termino_confirmacao or date.today()
    if date.today() >= inicio and date.today() <= termino:
        return True
            
            
def em_periodo_inscricao(db,atividade):
    """Se a atividade esta em periodo de inscricao"""
    termino = atividade_termino(db,atividade)
    
    #se a atividade já terminou não pode fazer a inscrição
    if termino < datetime.now(): return

    inicio = atividade.inicio_inscricao or datetime.today()
    termino = atividade.termino_inscricao or termino
    
    if datetime.today() >= inicio and datetime.today() <= termino:
        return True
        
        
def atividades_disponiveis(db,atividade,pessoa,pessoal=True,periodo_insc=True):#,limitante=False):
    """Retorna todas as atividades que a pessoa ainda pode se inscrever. 
       Não permite que uma pessoa se inscreva em uma atividade caso haja conflito de horario com outras
       atividades inscritas.
       ´´´pessoal´´´      : True ->> lista apenas as atividades que liberam inscricao online.
       ´´´periodo_insc´´´ : True ->> filtra somente as atividades que estao em periodo de inscricao """
    
    periodo = db.atividade_periodo
    
    grupo = db.grupo[atividade.grupo_id]
    q_ativs_inscritas = (db.inscrito.pessoa_id==pessoa.id) & \
                        (db.atividade.id==db.inscrito.atividade_id)
              
    #Não interessa os horários do evento e sim das atividades que fazem parte dele
    atividades_inscritas = db(q_ativs_inscritas & \
                              ~(db.atividade.tipo=='ev') ).select(db.atividade.ALL)
    
    ##Preparando a query das atividades disponiveis:
    n_periodo_inscricao=[0] ##variavel auxiliar que controla as atividades que NÃO estao em periodo de inscricao
    atividades_conflitantes = [0]
    
    #Verificando as atividades que acontecem no periodo que a pessoa está "livre"
    if len(atividades_inscritas):
    
        ##Apenas para inicializar a query. Não é necessário
        q_exclude_periodo = periodo.id > 0
        
        for ativ in atividades_inscritas:
            for p in db(db.atividade_periodo.atividade_id==ativ.id
                                 ).select(orderby=db.atividade_periodo.inicio):
                
                q_exclude_periodo = q_exclude_periodo | \
                      ( ((periodo.inicio <= p.inicio) & (periodo.termino > p.inicio)) | \
                        ((periodo.inicio < p.termino) & (periodo.termino >= p.termino) ))

        ##Atividades que conflitam o horario de realização
        atividades_conflitantes = db(q_exclude_periodo)._select(periodo.atividade_id, groupby=periodo.id)
        
        #Filtra somente as atividades do grupo que estão em periodo de inscrição!
        if periodo_insc:
            n_periodo_inscricao = db((db.atividade.id==periodo.atividade_id) & \
                                     (periodo.inicio < datetime.now()) )._select(db.atividade.id)
    
    return db(~q_ativs_inscritas & \
              ~db.atividade.id.belongs(atividades_conflitantes) & \
              ~db.atividade.id.belongs(n_periodo_inscricao) & \
              (db.atividade.grupo_id==grupo.id) ##Somente considera as atividades de um mesmo grupo.
              ).select(db.atividade.ALL,groupby=db.atividade.id), atividades_inscritas


def ja_inscrito_(db,atividade,pessoa):
    return db((db.inscrito.pessoa_id==pessoa.pessoa.id) & \
              (db.inscrito.atividade_id==atividade.id)).count()


def liberar_inscricao(db,atividade,pessoa=None,do_insc=False,check_insc=True):
    """Função que verifica se as inscricoes podem ou não ser liberadas para a atividade.
       Como criterio de liberacao estão o número de vagas disponiveis e se a atividade permite a
       lista de espera. Caso informado a ´´pessoa´´ verifica se o mesmo está ou não  inscrito.
       ´´´do_insc´´´ E se a função deve ou não levar em conta as datas previstas de inscrição
       check_insc se for True ele verifica tbm se a pessoa ja se inscreveu na atividade,
       caso contratio ver se ela poderia se inscrever"""

    if do_insc and not em_periodo_inscricao(db,atividade):
        return
    
    ja_inscrito = ja_inscrito_(db,atividade,pessoa)
                         
    if ja_inscrito and check_insc:
        return

#    if self.groups.count() and pessoa:
#        if not (pessoa.user and pessoa.user.groups.filter(
#                        id__in=self.groups.values_list('id',flat=True)).count() ):
#            return
    num_inscs = num_inscritos_(db,atividade)
    num_max = atividade.num_max or num_inscs + 1
    if (num_max <= num_inscs and atividade.espera) or (num_max > num_inscs): #caso as vagas ja tenham se esgotado
        return True
        

def inscricoes_finalizadas(db,atividade,pessoa):
    subatividade = db.atividade_subatividades
    return bool(db((db.inscrito.pessoa_id==pessoa.id) & \
                   (db.inscrito.finalizada==True) & \
                   (db.inscrito.atividade_id==db.atividade.id) & (
                   ((subatividade.mestra_id==atividade.id) & (subatividade.subatividade_id==db.atividade.id)) |\
                   ((subatividade.subatividade_id==atividade.id) & (subatividade.mestra_id==db.atividade.id)) )
                ).count() )
            

def finaliza_inscricoes(db,atividade,pessoa):
    subatividade = db.atividade_subatividades
    return db((db.inscrito.pessoa_id==pessoa.id) & \
              (db.inscrito.atividade_id==db.atividade.id) & (
              ((subatividade.mestra_id==atividade.id) & (subatividade.subatividade_id==db.atividade.id)) |\
              ((subatividade.subatividade_id==atividade.id) & (subatividade.mestra_id==db.atividade.id)) )
          ).update(db.inscrito.finalizada==True)
                
                
def insc_number(db,inscrito):
    atividade = inscrito.atividade_id
    n = 1 + db((db.inscrito.atividade_id==atividade.id) & \
               (db.inscrito.id < inscrito.id) & \
               (db.inscrito.fake==False)).count()
    if atividade.num_max:
        if inscrito.espera and n > atividade.num_max:
            return u'%iº Lista de espera' %(n - atividade.num_max)
    return n
    

def atividade_pagamento_(db,atividade):
    return db(db.atividade_pagamento.atividade_id==atividade.id).select().first()
    
                 
##Relativo aos boletos:
def boletos_(db,atividade,pessoa=None,grupo=None):
    """Funcao que retorna os boletos de 'pessoa' relativos a esta atividade"""
    
    q_bol = (db.atividade_boletos.atividade_id==atividade.id) & (db.boleto.id==db.atividade_boletos.boleto_id)
    
    if pessoa or grupo:
        pessoa_id = grupo.id_pessoa if grupo else pessoa.id

        q_bol = q_bol & (db.boleto.pessoa_id==pessoa_id)

    return  db(q_bol).select(db.boleto.ALL)


def valor_total_(db,atividade,pessoa):
    if not pessoa:
        return 0.
    
    atividade_pagamento = atividade_pagamento_(db,atividade)
    sum = db.atividade.valor.sum()
    subatividade = db.atividade_subatividades
    
    ##Todas as atividades relacionadas a atividade (para o caso de ser um evento)
    atividades_id = db((db.atividade.id==atividade.id) & (
                       ( (subatividade.mestra_id==atividade.id) & (subatividade.subatividade_id==db.atividade.id)) |\
                       ( (subatividade.subatividade_id==atividade.id) & (subatividade.mestra_id==db.atividade.id)) )
                       )._select(db.atividade.id)
    
    q = (db.atividade.id==db.inscrito.atividade_id) & \
        (db.inscrito.atividade_id.belongs(atividades_id)) & \
        (db.inscrito.espera==False)
    
    if atividade_pagamento and atividade_pagamento.gerar_boleto_por_grupo and 0:#and pessoa.is_integrante():
        pass
#        grupos = list(pessoa.integrante_set.all().values_list('grupo',flat=True) ) + \
#                 list(pessoa.tutor_set.all().values_list('grupo',flat=True) )
#        pessoas_id=[i.pessoa.id for i in chain(
#                                    Integrante.objects.filter(grupo__id__in=grupos),
#                                    Tutor.objects.filter(grupo_id__in=grupos) )]
#        return Inscrito.objects.filter( Q(Q(atividade__atividade__id=self.id)
#                                          | Q(atividade__id=self.id)),
#                                        pessoa__id__in=pessoas_id,
#                                        espera=False
#                ).aggregate(Sum('atividade__valor'))['atividade__valor__sum'] or 0.
    
    ##Se a pessoa for um grupo
    elif db(db.grupo.pessoa_id==pessoa.id).count():
        grupo = db(db.grupo.pessoa_id==pessoa.id).select().first()
        
        ##Todos os integrantes do grupo
        pessoas_id = db((db.integrante.grupo_id==grupo.id) & \
                            (db.integrante.tipo.belongs(['i','t'])))._select(db.integrante.pessoa_id)
        
        q = q & (db.inscrito.pessoa_id.belongs(pessoas_id))
    else:
        q = q & (db.inscrito.pessoa_id==pessoa.id)
    
    return db(q).select(sum).first()[sum] or 0.


def valor_residual_(db,atividade,pessoa=None):
    if pessoa:
        atividade_pagamento = atividade_pagamento_(db,atividade)
        if atividade_pagamento:
            ##valor relativo aos boletos sinalizados como pago. Notar que se for sinalizado
            ##e possuir um valor pago deve-se desconsiderá-lo nesta etapa
            q_bol = (db.atividade_boletos.atividade_id==atividade.id) & \
                    (db.boleto.id==db.atividade_boletos.boleto_id) & \
                    (db.boleto.pessoa_id==pessoa.id)
            q_sinalizado = (~(db.boleto.valor_pago.notnull) | (db.boleto.valor_pago==0.))  & \
                           (db.boleto.sinalizar_pago==True)
            q_pago = db.boleto.valor_pago > 0.
            
            sum = db.boleto.valor.sum()
            valor_pago = db(q_bol & (q_sinalizado | q_pago)
                            ).select(sum).first()[sum] or 0. ###groupby=db.boleto.id

            valor_residual = valor_total_(db,atividade,pessoa) - valor_pago

            return valor_residual if valor_residual > 0. else 0.
    else:
        return atividade.valor


def inscricao_pessoal(request,db,atividade,pessoa,insc_grupo=False,editar=False):
    ###O CODIGO DESTA FUNCAO PRECISA SER TODO REVISTO POIS EXISTE MTA COISA REDUNDANTE
    ###FUGINDO DAS BOAS PRATICAS DE PROGRAMACAO
    atividade_pagamento = atividade_pagamento_(db,atividade)
    insc_grupo = insc_grupo #and pessoa.is_integrante()
    do_insc = em_periodo_inscricao(db,atividade)
    ja_inscrito = ja_inscrito_(db,atividade,pessoa)
    submit_value='Inscrever-se'

    if request.vars.get('atividade_inscricao'):
        atividade_inscricao = db.atividade[request.vars('atividade_inscricao')] or redirect(URL('index') )
    else:
        atividade_inscricao = atividade
    
    permuta = not do_insc and atividade_inscricao.permuta ##Caso a atividade não esteja mais em periodo de inscricao e aceite permuta
    integrantes_inscritos = []
#    extra_filtro = Q()

#    if insc_grupo:
#        boletos = atividade.boletos(pessoa,pessoa.get_grupo() )
#        grupos = list(pessoa.integrante_set.all().values_list('grupo',flat=True) ) + \
#                 list(pessoa.tutor_set.all().values_list('grupo',flat=True) )
#        pessoas_id = [ i.pessoa.id for i in chain(
#                            Integrante.objects.filter(grupo__id__in=grupos),
#                            Tutor.objects.filter(grupo_id__in=grupos) ) ]

#        integrantes_inscritos = list(Inscrito.objects.filter(atividade=atividade_inscricao,
#                            pessoa__id__in=pessoas_id).values_list('pessoa',flat=True) )
#        extra_filtro = Q(Q(Q(atividade=atividade.id) |Q(atividade__atividade=atividade.id)) &
#                         Q(pessoa__id__in=pessoas_id))
#        grupos_finalizadas = all(Grupo_Inscricao.objects.filter(grupo__id__in=grupos,
#                    atividade=atividade).values_list('finalizada',flat=True) or [False])

#        if Grupo_Inscricao.objects.filter(atividade=atividade,grupo=pessoa.get_grupo()).count():
#            grupo_inscricao = Grupo_Inscricao.objects.get(atividade=atividade,grupo=pessoa.get_grupo())
#            n_pagos = grupo_inscricao.boletos().exclude(
#                Q(Q(valor_pago__isnull=False,valor_pago__gt=0.) |
#                  Q(sinalizar_pago=True)))

#            if n_pagos.count() > 1:
#                for b in n_pagos[:n_pagos.count()-1]:
#                    b.trash=True
#                    b.save()
#                ##Atualiza os boletos da pessoa
#                boletos = atividade.boletos(pessoa,pessoa.get_grupo() )

#            valor_total = grupo_inscricao.valor_total
#            valor_boletos = boletos.aggregate(Sum('valor'))['valor__sum'] or 0.

#            valor_residual = atividade.valor_residual(grupo_inscricao.grupo.id_pessoa)

#            if valor_total > valor_boletos and valor_residual:
#                novo = bool(not boletos.filter(sinalizar_pago=False).count() )#or grupo_inscricao.finalizada)
#                boleto = grupo_inscricao.get_numero_sequencial(novo=novo,update=grupo_inscricao.finalizada)
#                if not novo and grupo_inscricao.finalizada:
#                    messages.warning(request,u"Observe que o boleto %s pode ter sofrido alterações!" %boleto.nosso_numero_formatado)
#                boletos = atividade.boletos(pessoa,pessoa.get_grupo() )
#            elif valor_total < valor_boletos:
#                ##O boleto deve ser atualizado caso eles marquem o boleto como 'não pago'
#                ## e ainda exista um valor residual, ou caso o integrante nao informe
#                ## nada se admite quando existe boletos que nao foram pagos
#                update = bool(n_pagos.count())
#                novo=False
#                boleto = grupo_inscricao.get_numero_sequencial(update=update,
#                                                                novo=novo )
#                if update:
#                    messages.warning(request,u"Observe que o boleto %s pode ter sofrido alterações!" %boleto.nosso_numero_formatado)
#    else:
    ########-------------------
    boletos = boletos_(db,atividade,pessoa.pessoa)
    n_pagos = boletos.exclude(lambda row: ((db.boleto.valor_pago>0) | (db.boleto.sinalizar_pago==True)) )

    if len(n_pagos):
        for b in n_pagos[:len(n_pagos) - 1]:
            b.update_record(trash=True)

        ##Atualiza os boletos da pessoa
        boletos = boletos_(db,atividade,pessoa.pessoa)

    valor_total = valor_total_(db,atividade,pessoa.pessoa)
    
    valor_boletos = 0.
    for b in boletos: 
        valor_boletos+=b.valor

    valor_residual = valor_residual_(db,atividade,pessoa.pessoa)
    if atividade_pagamento and atividade_pagamento.forma_pagamento == "bo":
        if valor_total > valor_boletos and valor_residual:
            novo = bool( boletos.find(lambda row: db.boleto.sinalizar_pago==False).isempty() )#or grupo_inscricao.finalizada)
#            boleto = atividade.atividade_pagamento_.numero_sequencial(pessoa,novo=novo,update=atividade_inscricao.inscricoes_finalizadas(pessoa))
#            if not novo and atividade_inscricao.inscricoes_finalizadas(pessoa):
#                messages.warning(request,u"Observe que o boleto %s pode ter sofrido alterações!" %boleto.nosso_numero_formatado)
            boletos = boletos_(db,atividade,pessoa.pessoa)
        
        elif valor_total < valor_boletos:
            ##O boleto deve ser atualizado caso eles marquem o boleto como 'não pago'
            ## e ainda exista um valor residual, ou caso o integrante nao informe
            ## nada se admite quando existe boletos que nao foram pagos
            update = bool(not n_pagos.isempty())
            novo=False
#            boleto = atividade_pagamento.numero_sequencial(pessoa,novo=novo,update=update)

#            if update:
#                messages.warning(request,u"Observe que o boleto %s pode ter sofrido alterações!" %boleto.nosso_numero_formatado)
    ####--------------bloco identado para traz---------------------
    
    ##insc_ativ representa se o usuario ou integrante de seu grupo já foram inscritos nesta atividade
    insc_ativ = (not atividade_inscricao.requer_inscricao) or \
                bool( ja_inscrito or  (insc_grupo and len(integrantes_inscritos) ) )

    lib_inscricao = False
    if atividade_inscricao.insc_online or \
            atividade_inscricao.insc_online_subativs() and not insc_ativ:
        lib_inscricao = liberar_inscricao(db,atividade_inscricao,pessoa,do_insc=True,check_insc=True)

    bloquear = False
#    ##Verificando se o usuário se enquadra em nos grupos que a atividade permite se inscrever
#    if atividade_inscricao.groups.count():
#        if not (pessoa.user and pessoa.user.groups.filter(
#                    id__in=atividade_inscricao.groups.values_list('id',flat=True)).count() ):
#            bloquear = not insc_grupo

    #Filtra as atividades relacionadas a esta atividade que o usuário já se inscreveu
#    filtro = Q(Q(Q(atividade=atividade.id) |Q(atividade__atividade=atividade.id)) &
#                 Q(pessoa__user=request.user))
#    inscricoes = Inscrito.objects.filter(filtro | extra_filtro)
    action = request.post_vars.get('submit')
    print action,type(action),111111111111111111111111111111111111111
#    ##EFETIVANDO A INSCRIÇÃO
    if action:
        if action == 'Cancelar':
            redirect(URL('atividade','mostra_atividade',args=(atividade.slug,)) )

        elif action in ["Próximo passo","Inscreva-se","Salvar","Finalizar inscrição"]:
            ##Só inscreve a pessoa na atividade se a atividade requerer inscrição e se
            ##ela ainda não estiver inscrita. Observe o caso de ser um integrante de um grupo
            ##que pode estar efetivando a inscrição de outros integrantes na mesma atividade
            if atividade_inscricao.requer_inscricao and (not insc_ativ or insc_grupo):
                espera = False
#                pessoas_insc = 1
                pessoas_id = [pessoa.pessoa.id]

#                if insc_grupo:
#                    num_inscritos_inicial =  inscricoes.count() #Numeros de Inscritos dos Quais o Grupo "tem direito"

#                    form = InscGrupoAtividade(data=request.POST,pessoa=pessoa,
#                                              atividade=atividade_inscricao,
#                                              initial={'atividade':atividade_inscricao.id})
#                    if form.is_valid():
#                        pessoas_id = map(int, form.cleaned_data['pessoas'])
#                        pessoas_insc = Pessoa.objects.filter(id__in=pessoas_id)
#                        if pessoas_insc.count() > num_inscritos_inicial and permuta:
#                            removidos = pessoas_insc[num_inscritos_inicial:]
#                            for p in removidos:
#                                Inscrito.objects.filter(pessoa=p,
#                                                    atividade = atividade_inscricao).delete()
#                            messages.error(request,u"Você não pode selecionar um número de inscritos maior que o inicial. Pois as inscrições estão encerradas!")
#                            messages.error(request,u"As seguintes pessoas tiveram suas inscrições removidas: %s!" %','.join(map(unicode,removidos)))
#                            pessoas_insc = pessoas_insc[:num_inscritos_inicial]

#                    ##Removendo os integrantes que não estão inscritos
#                    for c in form.fields['pessoas'].choices:
#                        if not c[0] in pessoas_id:
#                            Inscrito.objects.filter(pessoa=c[0],
#                                                atividade = atividade_inscricao).delete()

                pessoas_insc = len(pessoas_id)
                ##Somente retornar a mensagem de erro caso apenas uma pessoa esta
                ##realizando a inscrição. Caso contrário deve-se proceder a inscrição
                ##até que as vagas se esgotem
                num_inscritos = num_inscritos_(db,atividade_inscricao,
                                        extra_query=~db.inscrito.pessoa_id.belongs(pessoas_id))
                if atividade_inscricao.num_max and \
                    (num_inscritos + pessoas_insc > atividade_inscricao.num_max ):
                    if not atividade_inscricao.espera:
                        if pessoas_insc > 1:
                            for pessoa in range(pessoas_insc):
                                if num_inscritos_(db,atividade_inscricao) < atividade_inscricao.num_max:
                                    insc = db.inscrito.update_or_insert(
                                                    pessoa=pessoa,
                                                    atividade = atividade_inscricao)
                                else: break
                            msg = u'Nem todos os integrantes selecionados puderam ser\
                                         inscritos pois as vagas se esgotaram.'
                        else:
                            msg = u'Vagas esgotadas'

                        session.messages = ('error',request,msg)
                        return locals()
                    else:
                        espera = True

                for pessoa_id in pessoas_id:
                    new_insc = db.inscrito.update_or_insert(pessoa_id=pessoa_id,atividade_id=atividade_inscricao.id)
                    if espera and new_insc:
                        if num_inscritos_(db,atividade_inscricao) > atividade_inscricao.num_max:
                            db.inscrito[new_insc].update_record(espera=True)

#                if espera:
#                    a = atividade_inscricao.inscritos().count()
#                    b = atividade_inscricao.num_max
#                    if pessoas_insc.count() > 1:
#                        msg = u"Algum dos integrantes selecionados estão na lista de espera \
#                                da atividade, pois as vagas disponíveis se esgotaram."
#                    else:
#                        msg = u'<i class="icon-circle-info"></i> Você foi inscrito nesta \
#                                atividade com sucesso. No entanto, você é o %sº da lista \
#                                de espera esteja atento caso surjam novas vagas' %(
#                                atividade_inscricao.inscritos().count() - atividade_inscricao.num_max)
#                    messages.warning(request, msg)
#                else:
#                    messages.success(request,"Inscrição efetuada com Sucesso!")

#                if insc_grupo:
#                    grupos = list(Integrante.objects.filter(pessoa__id__in=pessoas_id
#                                            ).values_list('grupo',flat=True) ) + \
#                             list(Tutor.objects.filter(pessoa__id__in=pessoas_id
#                                            ).values_list('grupo',flat=True) )
#                    grupos = Grupo.objects.filter(id__in=grupos)
#                    for grupo in grupos:
#                        grupo_inscricao = Grupo_Inscricao.objects.get_or_create(grupo=grupo,atividade=atividade)[0]
#                        if editar:
#                            grupo_inscricao.finalizada=False
#                        grupo_inscricao.inscritos = inscricoes
#                        grupo_inscricao.save()
#######################
            if not action == "Finalizar inscrição":
                return redirect(URL("") )#"%s%s" %(
#                            request.path,'?atividade_inscricao=%s' %request.GET.get('atividade_inscricao') if request.GET.get('atividade_inscricao') else "") )
           =´´´´´´´´´´´´´´´´´´´´´´ else:
                finaliza_inscricoes(db,atividade,pessoa.pessoa)
                
#                ##Caso seja um integrante inscrevendo o seu grupo finalizar a inscrição dos grupo
#                ##que tiveram seus integrantes selecionados por esta pessoa
                if insc_grupo:
                    pass
#                    for grupo in grupos:
#                        grupo_inscricao = Grupo_Inscricao.objects.get_or_create(grupo=grupo,atividade=atividade)[0]
#                        grupo_inscricao.finalizada=True
#                        grupo_inscricao.save()
#                        status_pagamento = request.POST.get('pago',"")

#                        if status_pagamento=='pago':
#                            boletos.update(sinalizar_pago=True)
#                        ##Adicionar verificação se a atividade exige boleto!
#                        valor_residual = atividade.valor_residual(grupo_inscricao.grupo.id_pessoa)
#                        n_pagos = grupo_inscricao.boletos().exclude(
#                                    Q(Q(valor_pago__isnull=False,valor_pago__gt=0.) |
#                                      Q(sinalizar_pago=True)))

#                        ##O boleto deve ser atualizado caso eles marquem o boleto como 'não pago'
#                        ## e ainda exista um valor residual, ou caso o integrante nao informe
#                        ## nada se admite quando existe boletos que nao foram pagos
#                        update = bool(status_pagamento=='update' and valor_residual) or n_pagos.count()
#                        novo=bool((status_pagamento=='pago' or not boletos.count()) and valor_residual)\
#                                    or ( not n_pagos.count() and valor_residual) #not update and
#                        boleto = grupo_inscricao.get_numero_sequencial(
#                                                                        update=update,
#                                                                        novo=novo )
#                        ##Remove o boleto apenas por seguranca!
#                        if boleto.valor==0. and not boleto.valor_pago and not boleto.sinalizar_pago:
#                            boleto.trash=True
#                            boleto.save()

#                        if update and not boleto.valor==0.:
#                            messages.warning(request,u"Observe que o boleto %s pode ter sofrido alterações!" %boleto.nosso_numero_formatado)
#                inscricoes.update(finalizada=True)
##                messages.success(request,u'<h4><i class="icon-ok"></i> Inscrição %s\
#                     com sucesso!</h4>' %('finalizada' if not editar else 'editada'))
#                if atividade.atividade_pagamento_ and atividade.atividade_pagamento_.forma_pagamento == "bo":
#                    messages.warning(request,u"<h4>Você deve pagar seu boleto até o dia %s!</h4>" \
#                     %date_filter(atividade.atividade_pagamento.data_vencimento,'d \d\e F \d\e Y') )
#                ## Remove o campo de edicao caso o inscrito esteja editando a inscrição
#                url = request.path.replace('editar/','')
                return redirect(URL('atividades','inscricao',args=(atividade.slug)) )#"%s%s" %(
#                                url,'?atividade_inscricao=%s' %request.GET.get(
#                                'atividade_inscricao') if request.GET.get('atividade_inscricao') else "") )

###    if insc_grupo:
###        form = InscGrupoAtividade(pessoa = pessoa,atividade=atividade_inscricao,
###                                  initial={'atividade':atividade_inscricao.id})

    insc_finalizadas = inscricoes_finalizadas(db,atividade,pessoa.pessoa)
#    valor_total = atividade.valor_total(pessoa)
    show_resumo = (not do_insc and not atividade_inscricao.permuta) or \
                  (insc_finalizadas and not insc_grupo and not editar) or \
                  (not lib_inscricao and not atividade.tipo == 'ev') or \
                  (insc_grupo and grupos_finalizadas and not editar) or \
                  bloquear

    ##Caso especifico onde nao se caracteriza edição mas os usuários removeram todos os integrantes
###    if insc_grupo and grupos_finalizadas and not editar and not inscricoes.count():
###        return HttpResponseRedirect(reverse('editar_inscricao_pessoal',args=(atividade.slug,)))
    pessoa_insc = pessoa
    return locals()
