#-*- coding: utf-8 -*-
from random import randint
from datetime import date
from gluon import URL,XML,I,current,redirect
T = current.T

def mail_send_mail(mail):
    ##Envia os emails
    if not mail.sended:
        mail_to,subject, message, reply_to = (mail_to,mail.assunto,mail.message,mail.mail_to)
        text_content = html_content = mail.conteudo

        sended = mail.send(mail_to,subject,message,
                           attachments = [mail.Attachment(f.arquivo) for f in mail.attachments] )
        if sended:
            mail.update_record(sended=sended,data_envio=date.now())

    return mail.sended


def mail_schedule(mail,db,user=None,acao_grupo=None,):
    ##Coloca o email na lista de emails pendente
    if user and not acao_grupo:
        acao_grupo=acao_grupo or db.acao_grupo.insert(user=user)
    elif not user and not acao_grupo:
        acao_grupo=acao_grupo or db.acao_grupo.insert()
    acao_grupo=acao_grupo or db.acao_grupo.insert(user=user)

    acao_id = db.acao.update_or_insert(table_name='mailmessage',object_id=mail.id)
    acao = db.acao[acao_id]  if acao_id else db((db.acao.table_name=='mailmessage') & (db.acao.object_id==mail.id)).select().first()

    ##Associando a acao a acao_grupo correspondente
    db.acao_grupo_acoes.update_or_insert(acao_grupo_id=acao_grupo.id,acao_id=acao.id)

#    if not acao_id:
        ##acao_id só existe se for criado nova acao. Quando é atualizado o retorno é None
#        acao.reset()  ##criar o metodo reset
#        if user:
#            acao.update_record(user=user)

def mail_process(mail,acao,acao_grupo):
    ##Processa o envio dos emails
    acao_grupo.update_record(comentario=u'Enviando email: <u>%s</u>' %mail.mail_to)
    if mail_send_mail(mail):
        acao_grupo.update_record(comentario=u'Email enviado com sucesso')
    else:
        acao.update_record(error=True)
        acao_grupo.update_record(comentario=u'Falha ao enviar email para %s' %mail.mail_to)

