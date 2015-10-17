# -*- coding: utf-8 -*-

# from gluon import current, A, URL
from gluon import IS_SLUG, current


INTEGRANTE_TIPO = dict(
    i='Integrante',
    ie='Integrante Egresso',
    t='Tutor',
    te='Tutor Egresso'
)

ATIVIDADE_TIPOS = {
    'ev':u'Evento',
    'pa':u'Palestra',
    'se':u'Seminário',
    'cu':u'Curso',
    'vi':u'Viagem',
    'cd':u'Credenciamento',
    'ps':u'Pesquisa',
    'ai':u'Atividade Interna',
    'ou':u"Outro"
}

ATIVIDADE_CLASSIFICACAO = {
    'en':u'Ensino',
    'ps':u'Pesquisa',
    'ex':u'Extensão',
    'tr':u'Ensino, Pesquisa e Extensao',
    'ot':u'Outros'
}

ATIVIDADE_DESCRICAO_COMMENT = (
    "Insira o máximo de informações relativas a esta atividade."
    "Este campo se transfomará na página inicial do perfil desta atividade."
)


def atividade_format(db, row):
    atividade = getattr(row, 'atividade', row)
    if atividade:
        return "%(nome)s" %atividade


def cidade_format(db, row):
    cidade = getattr(row, 'cidade', row)
    if cidade:
        estado = cidade.estado_id
        return "%s - %s" %(cidade.nome, estado.sgl)


def estado_format(db, row):
    estado = getattr(row, 'estado', row)
    if estado:
        return "%(nome)s - %(sgl)s" %(estado)


def grupo_format(db, row):
    grupo = getattr(row, 'grupo', row)
    if grupo:
        cidade = db.cidade[grupo.cidade_id]
        return "%s - %s" %(grupo.nome, db.cidade._format(cidade))


def grupo_nome_represent(db, nome, row):
    return "%s - %s" %(row['nome'], db.cidade._format(row['cidade_id']))


def grupo_slug_compute(db, row):
    return IS_SLUG()(
        "%s %s" %(row['nome'],
                  db.cidade._format(db.cidade[row['cidade_id']])
                  )
    )[0]

def mensagem_is_read(db, row):
    auth = current.auth
    pessoa_ = db((db.pessoa_fisica.pessoa_id==db.pessoa.id) & \
                (db.pessoa_fisica.user_id==auth.user_id)).select(db.pessoa_fisica.pessoa_id).first()
    if pessoa_:
        dst = db((db.mensagem_readers.mensagem_id==row.mensagem.id) & \
                 (db.mensagem_readers.pessoa_id==pessoa_.pessoa_id)).count()
        return dst or row.mensagem.de==pessoa_.pessoa_id


def mensagem_render_resposta(db, row, can_del):
    pessoa_ = db((db.pessoa_fisica.pessoa_id==db.pessoa.id) & \
                (db.pessoa_fisica.user_id==auth.user_id)).select().first()
    if pessoa_:
        q1 = (db.mensagem.resposta==row.mensagem.id) & (db.mensagem.id!=row.mensagem.id) #resposta
        q2 = (db.mensagem.id==db.mensagem_destinatarios.mensagem_id) & \
             (db.mensagem_destinatarios.pessoa_id==pessoa_.pessoa.id) #Se é destinatario
        q3 = db.mensagem.de==_pessoa.pessoa.id # se é autor da mensagem
        respostas = db(q1 & (q2 | q3)).select(db.mensagem.ALL,distinct=True)
        if respostas:
            html='<blockquote>'
            first=True
            for resp in respostas:
                context = dict(pessoa=pessoa_,mensagem=db.mensagem(resp.mensagem.id),
                               first=first,can_del=can_del)
                html+=response.render('default/message_reply.html',context)
                first=False
            return html
    return ""
