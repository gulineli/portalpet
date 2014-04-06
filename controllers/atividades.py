# coding: utf8
subatividade = db.atividade_subatividades
atividade_record = db(db.atividade.slug==request.args(0)).select().first()

if atividade_record:
    response.breadcrumbs = response.breadcrumbs or []
    response.breadcrumbs.append((URL(request.application,request.controller,'atividade',args=(atividade_record.slug,)), atividade_record.nome))

def atividade():
    from myutils import render_fields
    from atividade_utils import estagio_
    session.show_header_atividade=True
    
    atividade = atividade_record or redirect(URL('index'))
    
    action = request.vars.get('action','')
    e = request.vars.get('estagio','1')
    estagio = estagio_.get(e) or estagio_['1']
    
    if action in ('editar','criar'):
        response.title = "Nova Atividade" if action=='criar' else 'Editando  Atividade'
        
        if e =='5':
            table=db.atividade_congresso
            object_=db.atividade_congresso.update_or_insert(db.atividade_congresso.atividade_id==atividade.id)
        else:
            table=db.atividade
            object_=atividade
        
        form = SQLFORM(table, object_,showid=False,fields=estagio['fields'],buttons = [],)
        
        if e=='2':
            form[0].insert(0,LOAD('atividades','get_periodos.load',args=(atividade.slug,),
                                  _class="form-group") )
            
            
        if form.process().accepted:
            if action=='criar':
                response.flash=T('Atividade cadastrada com sucesso')
            else:
                response.flash=T('Dados atualizados com sucesso')
            if e=='5':
                redirect(URL('atividades','atividade',args=(atividade.slug,)))
            else:
                redirect(URL('atividades','atividade',args=(atividade.slug,),vars=dict(action='editar',estagio=int(e)+1)))
    else:
        response.title=''

    return locals()


def get_periodos():
    atividade = atividade_record or redirect(URL('index'))
    periodos=db(db.atividade_periodo.atividade_id==atividade.id).select()
    
    return locals()
    

def visao_geral():
    atividade = atividade_record or redirect(URL('index'))
    
    ##Obtendo a atividade Mestra:
    mestra = db((db.atividade_subatividades.subatividade_id==atividade.id) & 
                (db.atividade.id==db.atividade_subatividades.mestra_id)).select(db.atividade.ALL).first()
    if mestra:
        redirect(URL('atividades','visao_geral',args=(mestra.slug)) )
        
    q = db.atividade.id==atividade.id
#    if atividade.tipo == 'ev':
    q = q | ( ( atividade.id==db.atividade_subatividades.mestra_id) & 
              ( db.atividade.id==db.atividade_subatividades.subatividade_id) )

    atividades = db(q).select(db.atividade.ALL,groupby=db.atividade.id,orderby=db.atividade.nome)
    
    return locals()
    

def detalhes_participacao():
    atividade = atividade_record or redirect(URL('index'))
    
    return locals()


def inscricao_delta_chart():
    a = atividade_record
    if a:
        return locals()
    return 'Não encontrado!'
    

def set_atividade_header():
    if int(request.vars.show) >= 0:
        session.force_show_header_atividade = False
    else:
        session.force_show_header_atividade = True
    return ''


def comprovante_inscricao():
    from inscricao_utils import atividade_pagamento_
    from weasyprint import HTML
    
    atividade = atividade_record
    atividade_pagamento = atividade_pagamento_(db,atividade)
    
    response.headers['Content-Type']='application/pdf'
    response.headers['Content-Disposition'] = \
            'filename=comprovante_inscricao_%s_%s.pdf' %(
                            atividade.slug,
                            pessoa.pessoa.slug if pessoa else grupo.slug)

    insc_grupo = atividade_pagamento and \
                 atividade_pagamento.gerar_boleto_por_grupo #and \
#                 (not request.vars.get('pessoa') or pessoa.is_integrante())
    grupo_inscricao=None
#    grupo = pessoa.get_grupo() if pessoa else grupo

#    if insc_grupo and grupo and Grupo_Inscricao.objects.filter(atividade=atividade,grupo=grupo).count():
#        grupo_inscricao = Grupo_Inscricao.objects.get(atividade=atividade,grupo=grupo)

    filtro = ((( (subatividade.mestra_id==atividade.id) & (subatividade.subatividade_id==db.atividade.id)) |\
               ( (subatividade.subatividade_id==atividade.id) & (subatividade.mestra_id==db.atividade.id)) |\
               (db.atividade.id==atividade.id)) &\
             (db.inscrito.atividade_id==db.atividade.id ) &\
             (db.inscrito.pessoa_id==pessoa.pessoa.id) )
#    filtro = filtro & (db.inscrito.pessoa_id==pessoa.pessoa.id)

    inscricoes = db(filtro).select(groupby=db.inscrito.id)
    periodos = db((db.atividade_periodo.atividade_id==db.atividade.id) \
                  & filtro).select(db.atividade_periodo.ALL,groupby=db.atividade_periodo.id)
    requer_presenca = inscricoes.find(lambda row: row.atividade.frequencia_minima > 0)

    html  = response.render(locals())
    pdf = HTML(string=html).write_pdf()
    return pdf
        
        
##-------Inscrição--------------------------------------------------------------
def inscricao():
    
    atividade = atividade_record or redirect(URL('index'))
    
    ##Se a atividade está inserida em um evento então a inscrição só pode ser feita por lá!
    if db(db.atividade_subatividades.subatividade_id==atividade.id).count():
        mestra=db(db.atividade_subatividades.subatividade_id==atividade.id).select().first().mestra_id
        return redirect(URL('atividades','inscricao',args=(mestra.slug,)))

    tipo = request.args(1)
    editar = request.get_vars.get('editar')
    if tipo=='pessoal' or not tipo:
        from inscricao_utils import inscricao_pessoal
        from pessoa_utils import get_pessoa
        
        acesso = request.get_vars.get('acesso','restrito1')
        if acesso == 'restrito':
            pessoa = get_pessoa(request,db,auth,force_auth=True)
            return inscricao_pessoal(request,db,atividade,pessoa,insc_grupo=False,editar=editar,tipo=tipo)
        elif 1: ##Checar permissão do usuário logado
            pessoa = db.pessoa[request.post_vars.get("pessoa",pessoa)] if request.post_vars.get("pessoa") else None
#            response.views = 'atividades/inscricao_administrador.html'
            
#            pessoa = get_pessoa(request,db,auth,force_auth=True)
            return  inscricao_pessoal(request,db,atividade,pessoa,insc_grupo=False,editar=editar,tipo=tipo)
#    elif tipo==''


def get_pessoas_inscricao():
    import gluon.contrib.simplejson as sj
    
    atividade = db(db.atividade.id==request.args(0)).select().first()
    max_rows = int(request.vars.get('max_rows','15'))
    search_key = request.vars.get('search_key','')

    pessoas = db((db.pessoa.nome.contains(search_key))).select(db.pessoa.id,db.pessoa.nome,limitby=(0,max_rows),
                      orderby=db.pessoa.nome,groupby=db.pessoa.id,cacheable=True,
                      left=(db.pessoa_fisica.on(db.pessoa.id==db.pessoa_fisica.pessoa_id),
                            db.inscrito.on((db.inscrito.code_verification==search_key[:12]) &\
                                           (db.pessoa.id==db.inscrito.pessoa_id) ) ))
    pessoas_list = []
    for p in pessoas:
        parametros = {'id': p.id,'value': p.nome}
        if db((db.inscrito.atividade_id==atividade) & (db.pessoa.id==p.id)).count():
            parametros['title'] = "Pessoa já inscrita"
            parametros['class'] = "muted success"
        
        if atividade.tipo <> "ev":
            exclude_periodo=db.periodo.id==0
            for p in db(db.atividade_periodo.atividade_id==atividade.id).select(): #Leva em conta que os periodos são ordenados pela data
                exclude_periodo = exclude_periodo | (( (db.periodo.inicio <= p.inicio) & \
                                                       (db.periodo.termino >= p.inicio)) |\
                                                     ( (db.periodo.inicio <= p.termino) & \
                                                       (db.periodo.termino >= p.termino)) )

            ids = db(exclude_periodo)._select(db.periodo.id,groupby=db.periodo.id)
            s = (db.inscrito.atividade_id==db.atividade.id) & \
                (db.inscrito.pessoa_id==pessoa.id) & \
                (db.periodo.atividade_id==db.atividade.id) & \
                (db.periodo.id.belongs(ids))
            if db(s).count():
                parametros['title'] = "Horários conflitantes. (%s)" ','.join(db(s).select(db.atividade.nome))
                parametros['class'] = "disabled"
        
        pessoas_list.append(parametros)
        print parametros,888888888888
    
#    atividade = Atividade.objects.get(id=id_atividade)
#    if Inscrito.objects.filter(atividade=atividade,pessoa=pessoa).count():
#        return {'title':"Pessoa já inscrita",'class':"muted success"}

#    if atividade.natureza <> "ev":
#        exclude_periodo=Q()
#        for periodo in atividade.periodos.all(): #Leva em conta que os periodos são ordenados pela data
#            exclude_periodo = Q(exclude_periodo | Q(
#                                                    Q(inicio__lte=periodo.inicio,
#                                                     termino__gte=periodo.inicio) |
#                                                    Q(inicio__lte=periodo.termino,
#                                                     termino__gte=periodo.termino)
#                                                 ))

#        ids = Periodo.objects.filter(exclude_periodo).distinct().values_list('id', flat=True)

#        if Pessoa.objects.filter(id=pessoa.id,
#                    inscricao_pessoal__atividade__periodos__id__in = ids).count():
#            return {'title':"Esta pessoa está inscrita em outra atividade que conflita o horário com esta!",
#                    'class':"disabled"}
                    
    return sj.dumps(pessoas_list)
##Relativo a página pessoal
def pessoa_atividades():
    from pessoa_utils import get_pessoa
    from atividade_utils import (frequencia_participacao,listas_feitas,
        pessoa_get_certificados,certifica_inscrito)
    
    pessoa = get_pessoa(request,db,auth,force_auth=True)
    pessoa = pessoa or redirect(URL('index'))
    
    q_ativ = (db.inscrito.pessoa_id==pessoa.pessoa.id) &  \
             (db.atividade.id==db.inscrito.atividade_id) & \
             (db.atividade_periodo.atividade_id==db.atividade.id)
    
    ##Atividades Previstas
    ativ_prev = db( q_ativ & (db.atividade_periodo.inicio >= request.now) ).select(groupby=db.atividade.id) 
    ativ_real = db( q_ativ & (db.atividade_periodo.inicio < request.now) ).select(groupby=db.atividade.id) 

#    atividade_type = ContentType.objects.get_for_model(Atividade)
#    ##Atividades Organizadas pela pessoa
#    lotacoes = Lotacao.objects.filter(pessoa=pessoa,organizacao__content_type=atividade_type)

#    ativ_div = Atividade.objects.filter(periodos__inicio__gte=datetime.today(),
#                                        grupo__peoplegroups__user = request.user,
#                                        atividade__isnull=True).distinct()

#    if ativ_p.filter(confirmado=False,atividade__conf=True).count(): # Verifica se todas as atividades ja foram ou nao confirmadas
#        confirmacao='pendente'

#    if request.method=="POST":
#        postDict = request.POST.copy()

#        for key, value in postDict.items():
#            if key <>'salvar_prev':
#                a = Inscrito.objects.get(id = int(key))
#                a.data_conf = datetime.now()
#                a.save()
#                return HttpResponseRedirect(reverse('mostra_atividades_pessoa',args=(pessoa.slug,)) )
    return locals()


##-----------------------------------------------------------------------------
def resumo_participacao():
    atividade = atividade_record
    ##Se a atividade está inserida em um evento então mostre o resumo do evento!
#    if atividade.atividade_set.count()==1:
#        mestra=atividade.atividade_set.all()[0]
#        return HttpResponseRedirect(reverse('resumo_participacao',args=(mestra.slug,)))

#    insc_grupo = atividade.detalhe_pagamento_ and \
#                 atividade.detalhe_pagamento_.gerar_boleto_por_grupo

    inscritos_grupo=[]
#    if insc_grupo:
#        grupos_inscritos = Grupo_Inscricao.objects.filter(atividade=atividade).order_by('grupo__instituicao')
#        inscritos_grupo = list(grupos_inscritos.values_list('inscritos',flat=True) )
#    if request.method=="POST":
#        if request.POST.get('ajax') and request.POST.get('inscrito'):
#            tipo = request.POST.get('tipo')
#            ##Pode acontecer alguma coincidencia de id. Isso é um bug!!
#            if tipo=='numero_sequencial':
#                objeto = Numero_Sequencial.objects.get(id=request.POST.get('inscrito'))
#            elif tipo=='grupo_inscricao':
#                objeto = Grupo_Inscricao.objects.get(id=request.POST.get('inscrito') )
#            else:
#                objeto = Inscrito.objects.get(id=request.POST.get('inscrito'))

#            valor_total = objeto.valor_total

#            if valor_total <> objeto.valor_pago_total:
#                class_ = "success"
#                objeto.valor_pago = valor_total
#            else:
#                objeto.valor_pago = 0
#                class_ = "warning"
#            objeto.save()
#            receita_efetivada = atividade.receita_efetivada

#            data=dict(class_=class_,
#                      receita_efetivada = ("%.2f" %receita_efetivada).replace('.',','),
#                      valor = ('<h5><span class="edit" id="%s_%s_valor_pago">%.2f</span> / \
#                                    <small>%.2f</small></h5>' %(
#                                    tipo,objeto.id,objeto.valor_pago,valor_total)
#                            ).replace('.',',')
#                )
#            return HttpResponse(simplejson.dumps(data), mimetype='application/json')

    inscritos = db((( (subatividade.mestra_id==atividade.id) & (subatividade.subatividade_id==db.atividade.id)) |\
                   ( (subatividade.subatividade_id==atividade.id) & (subatividade.mestra_id==db.atividade.id)) |\
                   (db.atividade.id==atividade.id)) &\
                   (db.inscrito.atividade_id==db.atividade.id )).select(db.inscrito.ALL,groupby=db.inscrito.id)
             
#    Inscrito.objects.filter(Q(
#                                    Q(atividade__id=atividade.id)
#                                  | Q(atividade__atividade__id=atividade.id))
#                          ).distinct().exclude(id__in=inscritos_grupo or [0])


    return locals()
    
    
def pessoa_artigos():
    from pessoa_utils import get_pessoa
    from atividade_utils import versao_status,versao_editar,artigo_avaliacao_liberada,versao_prazo
    
    pessoa = get_pessoa(request,db,auth)
    pessoa = pessoa or redirect
    pessoal = pessoa == get_pessoa(request,db,auth,force_auth=True)
    artigos = db(db.artigo.dono_id==pessoa.pessoa.id).select()

    return locals()


def visualizar_artigo():
    pessoal = request.vars.get('pessoal',None)
    #request,slug,artigo,template_base="perfilAtividade.html"
#    pessoa = request.user.get_profile()
#    pessoa = get_pessoa(request,db,auth,force_auth=True)
#    pessoa = pessoa or redirect(URL('default','index'))
    
    artigo = db(db.artigo.id==request.args(0) ).select().first() or \
            redirect(URL('default','pessoa_artigos',args=(pessoa.pessoa.slug,)))

    from atividade_utils import versao_status,versao_editar,versao_prazo

    atividade = artigo.atividade_id
    versao = db(db.versao.artigo_id==artigo.id).select(orderby=~db.versao.revisao).first() ##Versao corrente
    
    response.title = 'Vizualizando artigo'
    if artigo.dono_id == pessoa.pessoa:# or request.user.is_superuser:
#        if request.method == "POST":
#            if request.POST.get('submit','')=="Enviar":
#                versao.enviado = True
#                versao.save()
#                messages.success(request,"Artigo enviado com sucesso! Obrigado.")
#                return HttpResponseRedirect(reverse('artigos_pessoal',args=(atividade.slug,)) )
#        return render_to_response('atividade/congresso/visualizar_artigo.html',locals(),
#                                  context_instance = RequestContext(request))
        return locals()
    return locals()
    ##Caso a pessoa não tenha permissão apra ver o artigo
#    else:
#        messages.error(request,u"Você não pode entrar aqui!")
#        return HttpResponseRedirect(reverse('artigos_pessoal',args=(atividade.slug,)) )
