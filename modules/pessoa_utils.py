#-*- coding: utf-8 -*-
from gluon import URL,XML,I,current,redirect

T = current.T

def get_pessoa(request,db,auth,select_args=[],select_kwargs={},force_auth=False,render=False):
    select_args = select_args # or [db.pessoa.ALL]
    if request.args(0) and not force_auth:
        arg = request.args(0)
        pessoas = db(((db.pessoa.slug==arg) | (db.pessoa.id==arg if arg.isdigit() else 0)) & \
                  (db.pessoa_fisica.pessoa_id==db.pessoa.id)).select(
                    *select_args,**select_kwargs)
        
    else:
        pessoas = db((db.pessoa_fisica.pessoa_id==db.pessoa.id) & \
                   (db.pessoa_fisica.user_id==auth.user_id)).select(
                    *select_args,**select_kwargs )
     
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


def pessoa_menu(response,auth):
    response.menu = [
        ((I(_class="icon-user"),' ',T('Perfil')), False, URL('default', 'pessoa'), []),
        ((I(_class="icon-list"),' ',T('Atividades')), False, URL('default','pessoa_atividades'),[]),
        ((I(_class="icon-file"),' ',T('Artigos')), False, URL('default','pessoa_artigos'),[]),
        #((I(_class="icon-blog"),' ',T('Arquivos/Apostilas')), False, URL('default','arquivos_pessoa'),[]),
        ((I(_class="icon-envelope"),' ',T('Mensagens')), False, URL('default','inbox'),[]),
        #((I(_class="icon-book-open"),' ',T('Albuns')), False, URL('default','albuns'),[]),

    ]

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
