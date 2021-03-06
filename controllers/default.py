# -*- coding: utf-8 -*-

from pessoa_utils import get_pessoa, get_mensagem
from portal_utils import portal_menu


pessoa_record = get_pessoa(request, db, auth)
response.subtitle = pessoa_record.pessoa.nome if pessoa_record else "Anônimo"


def index():
    """
    return auth.wiki()
    """
    response.subtitle = "Um caminho para a comunicação universitária"
    response.flash = T("Welcome to web2py!")
    return locals()


def home():
    return locals()


def pessoa():
    print get_pessoa(request, db, auth), auth.is_logged_in(), 888898282988
    if not get_pessoa(request, db, auth):
        redirect(URL('index') )

    from myutils import render_fields,copydata
    response.title = "Perfil"

    layout='simple_layout.html' if 'desmiss' in request.vars else 'layout.html'
    action = request.vars.get('action','')
    if action=='criar':
        response.title = "Nova Pessoa"
        form = SQLFORM(db.pessoa_fisica,upload=URL('download'))
    elif action=='editar':
        response.title = 'Editar Pessoa'
        response.view = "default/pessoa_edit.html"

        pessoa = get_pessoa(request, db, auth, render=False)


        if request.env.request_method=="POST":
            if request.vars.foto=='':
                request.vars.pop('foto')
            else:
                request.vars.update({'foto':db.pessoa.foto.store(request.vars.foto, request.vars.foto.filename)})

            ret = db(db.pessoa.id==pessoa.pessoa.id)\
                    .validate_and_update(**db.pessoa._filter_fields(request.vars))

            ret.update(db(db.pessoa_fisica.id==pessoa.pessoa_fisica.id)\
                        .validate_and_update(**db.pessoa_fisica._filter_fields(request.vars)))

            pessoa = pessoa_record = db(db.pessoa.id==pessoa.pessoa.id).select().first()
            if not ret.errors:
                redirect(URL('default','pessoa',args=(pessoa.slug)) )
                response.flash='Dados Atualizados com sucesso'

#        form = SQLFORM(db.pessoa_fisica,p.pessoa_fisica,upload=URL('download'),showid=False)
#         form = SQLFORM.factory(db.pessoa,db.pessoa_fisica,table_name='pessoa',
#                                upload=URL('download'),
#                                uploadfolder=os.path.join(request.folder,'uploads','users','photos'))
    else:
        pessoa_record = get_pessoa(request,db,auth,render=True)


#    if action in ('editar','criar'):
#        if form.process().accepted:
#            if action=='criar':
#                id = db.pessoa.insert(**db.pessoa._filter_fields(form.vars))
#                form.vars.pessoa_id=id
#                id = db.pessoa_fisica.insert(**db.pessoa_fisica._filter_fields(form.vars))
#                response.flash='Pessoa cadastrada com sucesso'
#            else:
#                 pessoa_record.pessoa.update_record(**db.pessoa._filter_fields(form.vars))
#                 pessoa_record.pessoa_fisica.update_record(**db.pessoa_fisica._filter_fields(form.vars))
#                response.flash='Dados Atualizados com sucesso'
#            redirect(URL('default','pessoa'))

#    dbg.set_trace()


    return locals()


def pessoa_atividades():
    return locals()


def pessoa_atividades():
    return locals()


def pessoa_artigos():
    return locals()


@breadcrumb()
#@login_required
def inbox():
    response.title = 'Mensagens'
    message_box_url = URL('message_box',args=(pessoa_record.pessoa.slug,) )

    s = db((db.mensagem_destinatarios.pessoa_id==pessoa_record.pessoa.id) &
           (db.mensagem.id==db.mensagem_destinatarios.mensagem_id) &
           (db.mensagem.master==None) )

    orderby = getattr(db.mensagem,request.vars.get('o','hora') )
    if orderby == db.mensagem.hora:
        orderby = ~orderby
    paginate = Paginate(request, s,
                        select_args=[db.mensagem.ALL],
                        select_kwargs={'orderby':orderby})
    mensagens = paginate.rows

    return locals()


def message():
    # Uma vez aberta a mensagem ele será considerada como lida
    reader = get_pessoa(request,db,auth,force_auth=True)

    # adicionar permissoes de leitura
    mensagem = db(db.mensagem.hash==request.vars.get('message')).select().first()
    mensagens_relacionadas = db(((db.mensagem.master==mensagem.id) |
                                (db.mensagem.id==mensagem.id)) & \
                                (((db.mensagem_destinatarios.mensagem_id==db.mensagem.id) &
                                (db.mensagem_destinatarios.pessoa_id==reader.pessoa.id)) |
                                (db.mensagem.de==reader.pessoa.id))  ).select(db.mensagem.ALL,orderby=~db.mensagem.hora,distinct=True)

    for m in mensagens_relacionadas:
        if not db((db.mensagem_readers.mensagem_id==m.id) & \
                  (db.mensagem_readers.pessoa_id==reader.pessoa.id)).count():
            db.mensagem_readers.insert(mensagem_id=m.id, pessoa_id=reader.pessoa.id)

    return locals()


#@login_required
def readed_message():#request,pessoa,mensagem,next=None
    mensagem = get_mensagem(request,db) or redirect(URL('message_box'))

    if not db((db.mensagem_readers.mensagem_id==mensagem.id) & \
              (db.mensagem_readers.pessoa_id==pessoa_record.pessoa.id)).count():
        db.mensagem_readers.insert(mensagem_id=mensagem.id, pessoa_id=pessoa_record.pessoa.id)

    response.flash='Mensagem marcada como lida com sucesso!'

    if 'ajax' in request.get_vars: return XML()

    redirect( request.get_vars.get('next', URL('message_box',args=(pessoa_record.pessoa.slug,)) ) )


#@login_required
def delete_message():
    mensagem = get_mensagem(request,db)

    db((db.mensagem_readers.mensagem_id==mensagem.id) & \
       (db.mensagem_readers.pessoa_id==pessoa_record.pessoa.id)).delete()
    db((db.mensagem_destinatarios.mensagem_id==mensagem.id) & \
       (db.mensagem_destinatarios.pessoa_id==pessoa_record.pessoa.id)).delete()

    #caso a mensagem não tenha mais destinatários
    if not db(db.mensagem_destinatarios.mensagem_id==mensagem.id).count() \
         or mensagem.de==pessoa_record.pessoa.id:
        mensagem.delete_record()
    response.flash = 'Mensagem apagada com sucesso!'

    redirect( request.get_vars.get('next', URL('inbox') ) )


#@login_required
def send_message():
    master = db(db.mensagem.hash==request.get_vars.get('master')).select().first()
    de = get_pessoa(request,db,auth,force_auth=True)

    db.mensagem.assunto.default = request.post_vars.get('assunto') or request.get_vars.get('assunto')
    db.mensagem.de.default = de.pessoa.id
    db.mensagem.master.default = master
    db.mensagem.de.readable=db.mensagem.de.writable=False

    form = SQLFORM(db.mensagem,_action=URL('default','send_message',vars=request.get_vars))

    destinatario=request.get_vars.get('destinatario')
    if master:
        destinatarios = db(((db.mensagem.id==master.id) | (db.mensagem.master==master)) &
                            (db.mensagem_destinatarios.mensagem_id==db.mensagem.id) &
                            (db.mensagem_destinatarios.pessoa_id!=de.pessoa.id) &
                            (db.pessoa.id==db.mensagem_destinatarios.pessoa_id)).select(db.pessoa.ALL,distinct=True)
    elif destinatario:
        destinatarios = db(db.pessoa.id==destinatario).select()
    else:
        destinatarios = db(db.pessoa.id==0).select()

    destinatario = destinatarios.first()

    if form.process().accepted:
        mensagem = form.vars.id
        for pessoa in destinatarios:
            db.mensagem_destinatarios.validate_and_insert(mensagem_id=mensagem,pessoa_id=pessoa)

        session.flash = 'Mensagem enviada com sucesso'
        next = request.vars.get('next')
        redirect(next or URL('default','inbox') )

    return locals()

def gustavo():
    return "PET"


@breadcrumb()
def grupos():
    response.title = 'Grupos Cadastrados'
    response.subtitle = ''
    portal_menu(response,auth)
    s = db(db.grupo.ativo==True)
    paginate = Paginate(request,s,select_args=[db.grupo.ALL],
                        select_kwargs={'orderby':db.grupo.nome},itens_page=16,
                        search_url=URL('default','get_grupo'),
                        info="%s %%{grupo[0]}" )
    response.paginate = paginate.render()
    grupos = paginate.rows

    return locals()


def get_destinatarios():
    import gluon.contrib.simplejson as sj

    max_rows = int(request.vars.get('max_rows','15'))
    search_key = request.vars.get('search_key','')

    pessoas_id = db(db.pessoa_fisica)._select(db.pessoa_fisica.pessoa_id)
    pessoas = db((db.pessoa.nome.contains(search_key)) &
                 (db.pessoa.id.belongs(pessoas_id)) ).select(db.pessoa.id,db.pessoa.nome,limitby=(0,max_rows),orderby=db.pessoa.nome).render()
    results = sj.dumps([
            {
                'id': p.id,
                'value': p.nome
            } for p in pessoas
        ])

    return results


def get_cidade():
    import gluon.contrib.simplejson as sj

    max_rows = int(request.vars.get('max_rows','15'))
    search_key = request.vars.get('search_key','')

    cidades = db(db.cidade.nome.contains(search_key)).select(db.cidade.id,db.cidade.nome,limitby=(0,max_rows),orderby=db.cidade.nome).render()
    results = sj.dumps([
            {
                'id': c.id,
                'value': c.nome
            } for c in cidades
        ])

    return results


def get_grupo():
    import gluon.contrib.simplejson as sj

    max_rows = int(request.vars.get('max_rows','15'))
    search_key = request.vars.get('search_key','')

    grupos = db(db.grupo.nome.contains(search_key)).select(db.grupo.id,db.grupo.nome,db.grupo.cidade_id,db.grupo.slug,limitby=(0,max_rows),orderby=db.grupo.nome).render()
    results = sj.dumps([
            {
                'id': g.id,
                'value': db.grupo._format(db.grupo[g.id]),
                'href': URL('grupos','grupo',args=(g.slug,))
            } for g in grupos
        ])

    return results


def get_atividade():
    import gluon.contrib.simplejson as sj

    max_rows = int(request.vars.get('max_rows','15'))
    search_key = request.vars.get('search_key','')

    atividades = db(db.atividade.nome.contains(search_key)).select(db.atividade.id,db.atividade.nome,db.atividade.slug,limitby=(0,max_rows),orderby=db.atividade.nome)
    results = sj.dumps([
            {
                'id': a.id,
                'value': a.nome,
                'href': URL('atividades','atividade',args=(a.slug,) )
            } for a in atividades
        ])

    return results


def generic_search():
    import gluon.contrib.simplejson as sj
    import time
    response.extension = "html"

    start_time = time.time()

    search_key = request.vars.get('q','')
    max_rows = int(request.vars.get('max_rows','15')) if search_key else 20.

    if search_key:
        cidades_id = db(db.cidade.nome.contains(search_key)).select(db.cidade.id).column()
        query = (
            (db.grupo.nome.contains(search_key)) |
            (db.grupo.cidade_id.belongs(cidades_id))
        )
    else:
        query = (db.grupo.id > 0)
    # Grupos
    grupos = db(query).select(db.grupo.ALL, limitby=(0, max_rows),
                              orderby=db.grupo.nome, groupby=db.grupo.id)

    print "--- %s seconds ---" % (time.time() - start_time),11
    start_time = time.time()

    results = [
        {'label': db.grupo._format(grupo),
         'value': URL('grupos', 'grupo', args=(grupo.slug,), extension="html")
        } for grupo in grupos
    ]

    print "--- %s seconds ---" % (time.time() - start_time),112
    start_time = time.time()

    # Pessoas
    pessoas = db(
        db.pessoa.nome.contains(search_key)
    ).select(limitby=(0,max_rows), orderby=db.pessoa.nome)

    results += [
        {'label': p.nome,
         'value': URL('default','pessoa',args=(p.slug,))
        } for p in pessoas
    ]
    print "--- %s seconds ---" %(time.time() - start_time),22
    start_time = time.time()

    # Atividades
    atividades = db(
        db.atividade.nome.contains(search_key)
    ).select(limitby=(0, max_rows), orderby=db.atividade.nome)

    results += [
            {
                'label': db.atividade._format(atividade),
                'value': URL('atividades','atividade',args=(atividade.slug,))
            } for atividade in atividades
        ]

    print "--- %s seconds ---" %( time.time() - start_time),33
    start_time = time.time()

    r = sj.dumps( results )
    print "--- %s seconds ---" % (time.time() - start_time),44

    return r


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    if request.args(0)=='login':
        response.view = "default/login2.html"
        db.auth_user.username.label = T("Username or Email")
        auth.settings.login_userfield = 'username'
        
        if request.vars.username and not IS_EMAIL()(request.vars.username)[1]:
            auth.settings.login_userfield = 'email'
            request.vars.email = request.vars.username
            request.post_vars.email = request.vars.email
            request.vars.username = None
            request.post_vars.username = None
        
        return dict(form=auth.login())

    return dict(form=auth())


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())


def jeditable():
    from myutils import jeditable_func
    return jeditable_func(globals(),request)
