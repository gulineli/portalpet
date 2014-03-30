# coding: utf8

grupo_record = db(db.grupo.slug==request.args(0)).select().first()

if grupo_record:
    response.breadcrumbs.append((URL(request.application,request.controller,'grupo',args=(grupo_record.slug,)), grupo_record.nome))
    response.subtitle = grupo_record.nome


def teste():
    return locals()


def index():
    redirect(URL('default','grupos'))
    return locals()


def grupo():
    from myutils import render_fields
    action = request.vars.get('action','')
    grupo = grupo_record or redirect(URL('index'))

    if action in ('editar','criar'):
        response.title = "Novo Grupo" if action=='criar' else 'Editando Grupo'
        form = SQLFORM(db.grupo, grupo,formstyle=bootstrap3,showid=False)

        if form.process().accepted:
            if action=='criar':
                response.flash=T('Grupo cadastrado com sucesso')
            else:
                response.flash=T('Dados atualizados com sucesso')
            redirect(URL('grupos','grupo',args=(grupo.slug,)))
    else:
        response.title=''

    return locals()


@breadcrumb()
def junte_se_a_nos():
    response.title = "Junte-se a nós"
    from pessoa_utils import get_pessoa
    from pendform_utils import PendForm
    grupo = grupo_record or redirect(URL('index'))
    pessoa = get_pessoa(request,db,auth,force_auth=True)

#    if pessoa.is_integrante():
#        pass
        #return HttpResponseRedirect(reverse('grupo_detail',args=(pessoa.get_grupo().slug,)) )

    edicao=True
    submit_value = 'Enviar'

    juntarse_grupo = db((db.juntarse_grupo.grupo_id==grupo.id) & (db.juntarse_grupo.pessoa_id==pessoa.id)).select().first()
    pendedform_id = juntarse_grupo.form_id if juntarse_grupo else None

    pendedform = PendForm(db,
                          pendedform=db(db.pendedform.id==pendedform_id).select().first(),
                          table_name='integrante')

    if juntarse_grupo:
        submit_value = "Salvar"
        response.flash = u"Sua solicitação já foi enviada. Você poderá modificá-la abaixo ou então aguardar até que um dos integrantes de seu grupo valide sua solicitação. Para cancelar a sua solicitação, clique em 'Cancelar'."
    form = pendedform.form
    form.vars.grupo_id=grupo.id
    form.vars.pessoa_id=pessoa.id

    if form.validate():
        from general_utils import mail_schedule
        pendedform.create_or_update(form.vars)
        id_j = db.juntarse_grupo.update_or_insert(grupo_id=grupo.id,
                                                  pessoa_id=pessoa.id,
                                                  form_id=pendedform.pendedform_id,
                                                  rejeitada=False)

        url = URL('grupos','validar_inclusao',args=(grupo.slug,id_j),scheme=True, host=True)
        message = HTML(P("%s solicitou sua inclusão no grupo. Caso esta pessoa faça parte de seu grupo, proceda a validação." %pessoa.nome),
                        P("Segue link para validação:",A(url,_href=url)) )
        subject=u'Solicitação de Inclusão no Grupo'

        mail_id = db.mailmessage.update_or_insert(
                        (db.mailmessage.subject==subject) &
                        (db.mailmessage.message==message) &
                        (db.mailmessage.mail_to==grupo.email),
                        subject=subject,message=message,mail_to=grupo.email)
        mail = db((db.mailmessage.subject==subject) & (db.mailmessage.message==message) &
                  (db.mailmessage.mail_to==grupo.email)).select().first()

        acao_grupo = db.acao_grupo.insert(titulo="Enviando solicitacao para email do grupo",user_id=auth.user)
        mail_schedule(mail,db,auth.user,acao_grupo)

        response.flash = u"Solicitação enviada com sucesso. Aguarde até que algum integrante do grupo autentique sua solicitação. Obrigado."

    return locals()


@breadcrumb()
def validar_inclusoes():
    grupo = grupo_record or redirect(URL('index'))
    solicitacoes = db((db.juntarse_grupo.grupo_id==grupo.id) &
                      (db.pessoa_fisica.pessoa_id==db.juntarse_grupo.pessoa_id)).select()
    if request.vars.solicitacao:
        from pendform_utils import PendForm
        solicitacao = db.juntarse_grupo[request.vars.solicitacao]
        pessoa_fisica = db(db.pessoa_fisica.pessoa_id==solicitacao.pessoa_id).select().first()
        pendedform = PendForm(db,pendedform=solicitacao.form_id,table_name='integrante')
        form = pendedform.form
        ##if form.process(): ##Promove a inserção dos dados na tabela final

    return locals()


@breadcrumb()
def integrantes():
    grupo = grupo_record or redirect(URL('index'))
    tipo = request.args(1) or ''
    integrante_query = (db.integrante.grupo_id==grupo.id) & (db.pessoa.id==db.integrante.pessoa_id) & (db.pessoa_fisica.pessoa_id==db.pessoa.id)
    tipo_query = (db.integrante.tipo=='t'+tipo) | (db.integrante.tipo=='i'+tipo)

    integrantes = db(integrante_query & tipo_query ).select(orderby=(~db.integrante.tipo,db.pessoa.nome),groupby=db.pessoa.id)  ## distinct=db.pessoa.id,
    response.title='Integrantes do grupo' if tipo=='' else 'Egressos do Grupo'
    
    return locals()


@breadcrumb()
def atividades():
    from atividade_utils import periodos_shortcut

    grupo = grupo_record or redirect(URL('index'))
    atividades = db(db.atividade.grupo_id==grupo.id).select()
    response.title='Atividades do Grupo'

    return locals()


@breadcrumb()
def arquivos():
    grupo = grupo_record or redirect(URL('index'))

    arquivos = db(db.arquivo_grupo.grupo_id==grupo.id).select()
    response.title='Arquivos do Grupo'

    return locals()


@breadcrumb()
def nova_reuniao():
    from pessoa_utils import get_pessoa
    pessoa = get_pessoa(request,db,auth,force_auth=True)
    grupo = grupo_record or redirect(URL('index'))
    reunioes_set = db((db.reuniao.grupo_id==grupo.id) & (db.reuniao.termino==None))
    if reunioes_set.count():
        response.flash = H3("Antes de inicar uma nova reunião você deverá encerrar essa reunião")
        redirect(URL('grupos',"encerra_reuniao",
                     args=(grupo.slug,reunioes_set.select(db.reuniao.ALL).first().hash)) )

    response.title="Iniciando reunião"
    
    db.reuniao.pauta_id.requires=IS_IN_DB(db(db.pauta.grupo_id==grupo.id),'pauta.id',db.pauta._format)
    
    form = SQLFORM(db.reuniao,fields=['pauta_id'],formstyle='bootstrap' )
    (form.vars.grupo_id,form.vars.secretario_id) = (grupo.id,pessoa.pessoa.id)

    if form.process().accepted:
        response.flash = T('Reunião criada com sucesso')
        reuniao = db.reuniao(form.vars.id)
        redirect(URL('grupos','reuniao',args=(grupo.slug,reuniao.hash)) )

    return locals()


@breadcrumb()
def reuniao():
    from gluon.contrib import simplejson
    from myutils import regroup
    grupo = grupo_record or redirect(URL('index'))
    reuniao = db(db.reuniao.hash==request.args(1)).select().first() or redirect(URL('grupos','reunioes',args=(grupo.slug,)))
    response.title = db.reuniao._format(reuniao)
    
#    if reuniao.termino:
#        from reuniao_utils import reuniao_create_arquivo
#        pdf = reuniao_create_arquivo(db,request,response,reuniao)
#        response.headers['Content-Type']='application/pdf'
#        response.headers['Content-Disposition'] = \
#                'filename=%s_%s.pdf' %(reuniao.number(),reuniao.inicio.year)
#        return pdf
        
#    if reuniao.termino:
#        return redirect(URL('grupos','reunioes', args=(grupo.slug,reuniao.hash)) )

    participantes = reuniao.participantes_set().select()
    
    ##Configurando as pautas que devem aparecer
    pautas_list = request.get_vars.get('pautas',[reuniao.pauta_id])
    initial = simplejson.dumps({'pautas':pautas_list})
    
    #Tópicos pendentes
    topicos_em_pauta = reuniao.topicos_set()._select(db.topico.id)
    topicos_pendentes = db((db.topico.grupo_id==grupo.id) & (db.topico.encerrado==False) &
                           (db.topico_pautas.topico_id==db.topico.id) & (db.pauta.id.belongs(list(pautas_list))) &
                           ~(db.topico.id.belongs(topicos_em_pauta))).select(db.topico.ALL,groupby=db.topico.id)
    return locals()


@breadcrumb()
def topico():
    from pessoa_utils import get_pessoa
    pessoa = get_pessoa(request,db,auth,force_auth=True).pessoa
    grupo = grupo_record or redirect(URL('index'))
    reuniao = db(db.reuniao.hash==request.args(1)).select().first() or redirect(URL('grupos','reunioes',args=(grupo.slug,)))
    topico = db(db.topico.id==request.args(2)).select().first()

    edicao = request.get_vars.get('edicao',False)
    reuniao_link = URL('grupos','reuniao',args=(grupo.slug,reuniao.hash),vars=request.get_vars)

    em_pauta = False ##True se o tópico estiver na pauta da reuniao em questão
    if topico:
        em_pauta = bool(reuniao.topicos_set(db.topico.id==topico.id).count())
        if em_pauta:
            response.title = "Editando Tópico:"
        else:
            response.title = "Discutindo Tópico:"
    else:
        response.title = "Criando novo Tópico:"

    fields=[db.topico.encerrado]
    if topico and (topico.responsaveis_set().count() or topico.limite):
        fields.append(db.topico.data_acao)

    form = SQLFORM(db.topico,topico,showid=False)
    form.vars.grupo_id = grupo.id

    if topico:
        historico = topico.posts_set(db.post.closed==False).select()
        post = historico.first()

        ##Populando os dados iniciais do formulario
        db.topico.data_acao.default=topico.data_acao
        db.topico.encerrado.default=topico.encerrado
        db.post.texto.default=post.texto if post else ''

        fields.append(db.post.texto)

        submit_button='Atualizar' if em_pauta else "Salvar e adicionar à Pauta"
        pForm = SQLFORM.factory(*fields,formstyle="bootstrap",submit_button=submit_button)
        pForm.add_button('Cancelar', reuniao_link,_class="btn")
        pForm[0][-1][1]['_class']='btn btn-primary pull-right'

        if pForm.process().accepted:
            post_data = dict(topico_id=topico.id,autor_id = pessoa.id)
            post_data.update(**db.post._filter_fields(pForm.vars))
            db.post.update_or_insert((db.post.id==(post.id if post else 0)),**post_data)
            topico.update_record(encerrado=pForm.vars.encerrado,data_acao=pForm.vars.data_acao)
            #Se o tópico não esta em pauta adicione-o
            if not em_pauta:
                db.reuniao_topicos.insert(reuniao_id=reuniao.id,topico_id=topico.id)
            session.flash = "Tópico atualizado com sucesso"

            redirect(reuniao_link)

    if form.process().accepted:
        if not topico:
            db.reuniao_topicos.insert(reuniao_id=reuniao.id,topico_id=form.vars.id)
            db.topico_pautas.insert(topico_id=form.vars.id,pauta_id=reuniao.pauta_id)
            session.flash = "Tópico criado com sucesso"
        else:
            session.flash = "Tópico atualizado com sucesso"
        redirect(reuniao_link)

    return locals()


def remove_topico():
    grupo = grupo_record or redirect(URL('index'))
    reuniao = db(db.reuniao.hash==request.args(1)).select().first() or redirect(URL('grupos','reunioes',args=(grupo.slug,)))
    topico = db(db.topico.id==request.args(2)).select().first() or redirect(URL('grupos','reunioes',args=(grupo.slug,)))
    db((db.reuniao_topicos.reuniao_id==reuniao.id) & (db.reuniao_topicos.topico_id==topico.id)).delete()
    redirect(URL('grupos','reuniao',args=(grupo.slug,reuniao.hash),vars=request.get_vars))


@breadcrumb()
def encerra_reuniao():
    grupo = grupo_record or redirect(URL('index'))
    reuniao = db(db.reuniao.hash==request.args(1)).select().first() or redirect(URL('grupos','reunioes',args=(grupo.slug,)))
    response.title="Reunião iniciada em %s" %date2str(reuniao.inicio)
    action = request.post_vars.get('submit')

    if action==u'Sim': #Encerando a reunião
        from reuniao_utils import reuniao_close
        ##Envia o email  e encerra a reuniao
        reuniao_close(db,request,response,reuniao)
        return redirect(URL('grupos','reunioes',args=(grupo.slug,)) )

    elif action=='Não': #Cancelando o encerramento
        return redirect(URL('grupos','reuniao',args=(grupo.slug,reuniao.hash)) )

    termino = reuniao.termino if reuniao.termino else request.now
    diff = termino - reuniao.inicio
    total_seconds = diff.seconds + diff.days * 24 * 3600
    alert_finished = True if total_seconds > 2*60*60 or total_seconds < 5*60 else False
    return locals()


def reunioes():
    response.title = 'Reuniões do Grupo'
    grupo = grupo_record or redirect(URL('index'))
    reunioes = db(db.reuniao.grupo_id==grupo.id).select(orderby=~db.reuniao.inicio)

    return locals()


def assunto():
    import gluon.contrib.simplejson as sj
    
    max_rows = int(request.vars.get('max_rows','15'))
    search_key = request.vars.get('search_key','')
    grupo_id = request.vars.get('grupo_id','')
    
    
    atividade_ids = db(db.atividade.nome.contains(search_key))._select(db.atividade.id)
    
    assuntos = db(( (db.assunto.table_name=='atividade') & (db.assunto.object_id.belongs(atividade_ids)) ) |
                  (db.assunto.assunto.contains(search_key)) & (db.assunto.grupo_id==grupo_id) 
                 ).select(
                         limitby=(0,max_rows),
                         orderby=db.assunto.assunto).render()
    results = sj.dumps([
            {
                'id': a.id,
                'value': a.assunto or 11
            } for a in assuntos
        ])
    
    return results
    
    
def jeditable():
    from myutils import jeditable_func
    return jeditable_func(globals(),request)
