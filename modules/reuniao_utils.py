#-*- coding: utf-8 -*-

from gluon import current,IS_SLUG#,redirect,URL,XML,I,
T = current.T

def reuniao_topico_set(db,row,extra_query=None):
    if extra_query:
        return db((db.reuniao_topicos.reuniao_id==row.reuniao.id) & (db.topico.id==db.reuniao_topicos.topico_id) & (extra_query))
    return db((db.reuniao_topicos.reuniao_id==row.reuniao.id) & (db.topico.id==db.reuniao_topicos.topico_id))


def reuniao_number(db,reuniao):
    year = reuniao.inicio.year
    return db((db.reuniao.grupo_id==reuniao.grupo_id) &
              (db.reuniao.inicio.year()==year) &
              (db.reuniao.inicio < reuniao.inicio)).count()


def reuniao_create_arquivo(db,request,response,reuniao):
    from utils import write_pdf
    grupo = reuniao.grupo_id
    pagesize = 'A4'
    html = response.render('grupos/reuniao_pdf.html', locals() )
    filename = u'Ata_Eletronica-%s_%s' %(reuniao.number(),reuniao.inicio.year)
    path = write_pdf(html,IS_SLUG()(filename)[0],base_folder='/tmp' )
    filename+='.pdf'
    arquivo = db.arquivo.insert(nome = filename,tipo=9,
                                arquivo = db.arquivo.arquivo.store(open(path, 'rb'), path))
    reuniao.update_record(arquivo_id = arquivo)
    return arquivo


def reuniao_close(db,request,response,reuniao):
    ##Finaliza a reunião
    if not reuniao.termino:
        reuniao.update_record(termino = request.now)

    ##Gera o pdf
    arquivo_id = reuniao_create_arquivo(db,request,response,reuniao) #Gera o arquivo em pdf e o relaciona nos arquivos do grupo


    ##Fechando os topicos para evitar que eles sejam editados nas reunioes seguintes
    for topico in reuniao.topicos_set().select(db.topico.ALL):
        topico.close(topico)

    #Enviando email para o grupo com o conteúdo da reunião
    html = response.render('grupos/reunioes_mailmessage.html',{reuniao:reuniao,db:db})
    assunto = db.reuniao._format(reuniao)
    db.mailmessage.update_or_insert(db.mailmessage.assunto==assunto,
                       assunto = assunto,
                       conteudo=html,
                       para = reuniao.grupo_id.email,
                       anexos=arquivo_id
    )

#        acao_grupo = Acao_Grupo.objects.create(titulo="Enviando ata por email",user=request.user)
#        mail.schedule(request.user,acao_grupo)

#        msg = u'<i class="icon-ok"></i> Reunião encerrada com sucesso! <br>\
#                Um email com essa ata está sendo enviado para o seu grupo'
#        messages.success(request, msg)

#    Adicionando as permissões ao arquivo criado - PENSAR EM COLOCAR ISSO EM OUTRO LUGAR!!!
#    integrante_grupo = GrupoUserGroup.objects.get(nome = "Integrantes",
#                                                  name='%s_integrantes' %grupo.slug)
#    arquivo_content_type = ContentType.objects. get_for_model(type(arquivo))

#    creator = Pessoa.objects.filter(Q(Q(integrante__grupo=grupo)| Q(tutor__grupo=grupo)))[0].user

#    codenames = ('arquivo_permission.change_arquivo',
#                 'arquivo_permission.browse_arquivo')
#    for codename in codenames:
#        custon_permission = CustomPermission.objects.get_or_create(
#                                              codename=codename,
#                                              content_type=arquivo_content_type,
#                                              creator=creator,
#                                              object_id=arquivo.id)[0]
#        custon_permission.groups.add(integrante_grupo)
#        custon_permission.save()


def reuniao_participantes_set(db,row,extra_query=None):
    return db((db.integrante.grupo_id==row.reuniao.grupo_id) &
              (db.integrante.tipo.belongs('t','i')) )

def reuniao_ausentes_set(db,row,extra_query=None):
    return db((db.reuniao_ausentes.reuniao_id==row.reuniao.id) & (db.pessoa.id==db.reuniao_ausentes.pessoa_id))


def topico_pautas_set(db,row,extra_query=None):
    return db((db.topico_pautas.topico_id==row.topico.id) & (db.pauta.id==db.topico_pautas.pauta_id))


def topico_responsaveis_set(db,row,extra_query=None):
    if extra_query:
        return db((db.topico_responsaveis.topico_id==row.topico.id) & (db.pessoa.id==db.topico_responsaveis.pessoa_id) & (extra_query))
    return db((db.topico_responsaveis.topico_id==row.topico.id) & (db.pessoa.id==db.topico_responsaveis.pessoa_id))


def topico_posts_set(db,row,extra_query=None):
    if extra_query:
        return db((db.post.topico_id==row.topico.id) & extra_query)
    return db(db.post.topico_id==row.topico.id)

def topico_status(topico):
    """Retorna o status do topico quanto a data limite de finalizacao do topico"""
    request = current.request
    today = request.now.date()
    if topico.limite:
        if topico.data_acao:
            if topico.data_acao < topico.limite:
                ##Concluiu no prazo
                return 'concluido no prazo'
            else:
                ##Concluiu fora do prazo determinados
                return 'com atraso'
        elif topico.limite < today:
            return 'pendente'
        else:
            return 'no prazo'


def topico_status_class(topico):
    """Esta funcao retorna a classe de alerta de acordo com o estado do topico.
    Topicos atrasados recebem o status de 'danger', concluidos com atraso 'warning', e
    os concluidos no prazo 'success'. Os topicos que nao tiverem informados uma data limite
    nao receberao nenhuma classificacao especial."""
    status = topico_status(topico)
    if status:
        status_class_dict = {
            'concluido no prazo':'success',
            'com atraso':'warning',
            'pendente':'danger',
            'no prazo':''
        }
        return status_class_dict[status]


def topico_responsaveis_representacao(db,topico):
    count = topico.responsaveis_set().count()
    if count > 2:
        integrantes_count = db(db.integrante.grupo_id==topico.grupo_id).count()
        if count == integrantes_count:
            return XML("Todos os integrantes")
        else:
            return XML(u', '.join([p.nome for p in topico.responsaveis_set().select(db.pessoa.ALL)]))
    return UL(*[p.nome for p in topico.responsaveis_set().select(db.pessoa.ALL)])


def topico_close(db,row,topico):
    topico.update_record(closed=True)
    topico.posts_set(db.post.closed==False).update(closed=True)
