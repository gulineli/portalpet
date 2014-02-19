# coding: utf8

atividade_record = db(db.atividade.slug==request.args(0)).select().first()
if atividade_record:
    response.breadcrumbs = response.breadcrumbs or []
    response.breadcrumbs.append((URL(request.application,request.controller,'atividade',args=(atividade_record.slug,)), atividade_record.nome))

def atividade():
    from myutils import render_fields
    session.show_header_atividade=True
    
    atividade = atividade_record or redirect(URL('index'))
    action = request.vars.get('action','')

    if action in ('editar','criar'):
        response.title = "Nova Atividade" if action=='criar' else 'Editando  Atividade'
        form = SQLFORM(db.atividade, atividade,formstyle='bootstrap',showid=False)

        if form.process().accepted:
            if action=='criar':
                response.flash=T('Grupo cadastrado com sucesso')
            else:
                response.flash=T('Dados atualizados com sucesso')
            redirect(URL('atividades','atividade',args=(atividade.slug,)))
    else:
        response.title=''

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
    

##-------Inscrição--------------------------------------------------------------
def inscricao():
    
##    ##Se a atividade está inserida em um evento então a inscrição só pode ser feita por lá!
##    if atividade.atividade_set.count()==1:
##        mestra=atividade.atividade_set.all()[0]
##        return HttpResponseRedirect(reverse('insc_atividade',args=(mestra.slug,)))
##        
    atividade = atividade_record or redirect(URL('index'))

    tipo = request.args(1)
    if tipo=='pessoal' or not tipo:
        from inscricao_utils import inscricao_pessoal
        from pessoa_utils import get_pessoa
        
        pessoa = get_pessoa(request,db,auth,force_auth=True)
##        pessoa = get_object_or_404(Pessoa,id=pessoa) if pessoa else request.user.get_profile()

        return inscricao_pessoal(request,db,atividade,pessoa,insc_grupo=False,editar=False)


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
