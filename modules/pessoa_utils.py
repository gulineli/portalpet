﻿#-*- coding: utf-8 -*-
from gluon import URL,XML,I,current,redirect

T = current.T

def get_pessoa(request, db, auth, select_args=[], select_kwargs={},
               force_auth=False, render=False):
    select_args = select_args # or [db.pessoa.ALL]
    if request.args(0):
        arg = request.args(0)
        pessoas = db(((db.pessoa.slug==arg) | (db.pessoa.id==arg if arg.isdigit() else 0)) & \
                  (db.pessoa_fisica.pessoa_id==db.pessoa.id)).select(
                    *select_args,**select_kwargs)

    else:  # if force_auth:
        pessoas = db((db.pessoa_fisica.pessoa_id==db.pessoa.id) & \
                     (db.pessoa_fisica.user_id==auth.user_id)).select(
                    *select_args,**select_kwargs )

    print pessoas, auth.user_id, 9999999999999999999999
    if render:
        return pessoas.render(0,fields=[db.pessoa.cidade_id,
                                        db.pessoa_fisica.sexo,
                                        db.pessoa_fisica.cidade_estudo_id,
                                        db.pessoa_fisica.data_nascimento]) if len(pessoas) else None
    else:
        return pessoas.first()


def get_mensagem(request,db,select_args=[],select_kwargs={}):
    return db(db.mensagem.hash==request.vars.get('mensagem')
                ).select(*select_args,**select_kwargs).first()


def pessoa_menu(db,response,auth):
    pessoa = db((db.pessoa_fisica.pessoa_id==db.pessoa.id) & \
                   (db.pessoa_fisica.user_id==auth.user_id)).select(db.pessoa.ALL).first()
    response.menu = [
        ((I(_class="fa fa-user"),' ',T('Perfil')), False, URL('default', 'pessoa'), []),
        ((I(_class="fa fa-list"),' ',T('Atividades')), False, URL('default','pessoa_atividades'),[]),
        ((I(_class="fa fa-file"),' ',T('Artigos')), False, URL('default','pessoa_artigos'),[]),
        #((I(_class="fa fa-blog"),' ',T('Arquivos/Apostilas')), False, URL('default','arquivos_pessoa'),[]),
        ((I(_class="fa fa-envelope"),' ',T('Mensagens')), False, URL('default','inbox'),[]),
        #((I(_class="fa fa-book-open"),' ',T('Albuns')), False, URL('default','albuns'),[]),
    ]

    integrantes = db(db.integrante.pessoa_id==pessoa.id).select(groupby=db.integrante.grupo_id)
    if pessoa and len(integrantes):
        for i in integrantes:
            grupo = i.grupo_id
            response.menu.append(
                ((I(_class="fa fa-group"),' ',grupo.nome), False,"",
                    [
                     (T('Página do Grupo'), False, URL('grupos','grupo',args=(grupo.slug,)),[]),
                     (T('Solicitações de Inclusão'), False, URL('grupos','grupo',args=(grupo.slug,)),[]),
                     (T('Caixa de entrada'), False, URL('grupos','grupo',args=(grupo.slug,)),[]),
                     (T('Atividades'), False, URL('grupos','grupo',args=(grupo.slug,)),[]),
                     (T('Arquivos'), False, URL('grupos','grupo',args=(grupo.slug,)),[]),
                     (T('Reunião'), False, URL('grupos','grupo',args=(grupo.slug,)),[]),
                     (T('Arquivos'), False, URL('grupos','grupo',args=(grupo.slug,)),[])
                     ]
                 )
            )

#MENSAGEM POST_SAVE
#for pessoa in destinatarios:
#                if pessoa.user:
#                    email = pessoa.user.email
#                    url = reverse("message_box",args=(pessoa.slug,))
#                else:
#                    email = pessoa.grupo_set.all()[0].email
#                    url = reverse("grupo_message_box",args=(pessoa.slug,))

#                mail = MailMessage.objects.create(assunto = u"Você recebeu uma mensagem no Portal Pet [%s]" %message.hora,
#                                                  conteudo = 'Sua caixa de entrada tem novas mensagens clique <a href="http://www.portalpet.feis.unesp.br%s">aqui</a> para lê-la(s)' %url,
#                                                  to = email)
#                acao_grupo = Acao_Grupo.objects.create(titulo="Enviando mensagem para %s" %email,user=request.user)
#                mail.schedule(request.user,acao_grupo)
