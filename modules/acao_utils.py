#-*- coding: utf-8 -*-
from random import randint

from gluon import URL,XML,I,current,redirect
T = current.T

def acao_grupo_progress(acao_grupo):
    """Retorna a porcentagem de acões concluidas"""
    acoes_concluidas = db(db.acao_grupo_acoes.acao_grupo_id==acao_grupo.id).count()
    return float(acoes_concluidas)/acao_grupo.acoes.count()


def acao_grupo_process(acao_grupo):
#        try:
    acao_grupo.estado = 'r'
    acao_grupo.save()
    for acao in acao_grupo.acoes.all():
        acao.reset()
        acao.process(acao_grupo)

    acao_grupo.estado = 'c'
#        except:
#            e = sys.exc_info()[1]
#            self.comentario = "Algum erro aconteceu com seu pedido, por favor informe os administradores"
#            self.estado = 'p'
#            self.error = True
#            self.errorinfo = e
    acao_grupo.data_processamento = datetime.datetime.now()
    acao_grupo.showed=None
    acao_grupo.save()
