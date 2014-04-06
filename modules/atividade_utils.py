#-*- coding: utf-8 -*-
from gluon import URL,XML,I,current,redirect
from custon_helper import AUTORIZED_MENU
from myutils import date2str

from datetime import datetime


## ordem_inscricao - insc_number

__all__ = ['atividade_menu','ordem_inscricao','frequencia_participacao','certifica_inscrito','pessoa_get_certificados',
           'num_inscritos_','num_presenca','listas_feitas','periodos_shortcut','atividade_inicio','atividade_termino',
           'em_periodo_inscricao','data_limite_avaliacao',
           'atividade_areas_conhecimento','data_limite_submissao','versao_dataRes','versao_editar','versao_status',
           'versao_prazo','artigo_avaliacao_liberada']


T = current.T


def atividade_menu(response,auth,atividade):
    response.menu = AUTORIZED_MENU([
        ##Junte-se a nos
        ((I(_class="icon-home"),' ',T('Informações')),
         False, URL('atividades', 'atividade',args=(atividade.slug,)), [],True),
         ##Inscrições
        ((I(_class="icon-group"),' ',T('Inscrição')),
         False, "",
         [
             ((T('Visão Geral')),False, URL('atividades', 'visao_geral',args=(atividade.slug,)), []),
             ((T('Inscrições')),False, URL('atividades', 'inscricao',args=(atividade.slug,)), []),
             ((T('Resumo de Participação')),False, URL('atividades', 'resumo_participacao',args=(atividade.slug,)), []),
             ((T('Comprovantes de Inscrição')),False, URL('atividades', 'comprovantes_inscricao',args=(atividade.slug,)), []),
             ((T('Lista Final')),False, URL('atividades', 'lista_final',args=(atividade.slug,)), []),
             ((T('Frequencia')),False, URL('atividades', 'frequencia',args=(atividade.slug,)), []),
             ((T('Falar com os Inscritos')),False, URL('atividades', 'falar_inscritos',args=(atividade.slug,)), []),
         ]),
        ##Programação
        ((I(_class="icon-calendar"),' ',T('Programação')),
         False, URL('atividades', 'programacao',args=(atividade.slug,)), [],True),
        ##Financeiro
        ((I(_class="icon-credit-card "),' ',T('Financeiro')),
         False, "",
         [
             ((T('Balanço')),False, URL('atividades', 'balanco_financeiro',args=(atividade.slug,)), []),
             ((T('Receitas')),False, URL('atividades', 'receitas',args=(atividade.slug,)), []),
             ((T('Despesas')),False, URL('atividades', 'despesas',args=(atividade.slug,)), []),
         ]),

    ]).autorized


estagio_ = {
        '1':{'fields':['tipo','classificacao','nome','obs','divulgar','mini_relatorio'],
#                       'atividade_periodo':['periodos'],
#                       'atividade_subatividades':['subatividade_id'],
             'mensagem':"Este é o mínimo que precisa definir para criar uma atividade" },

       '2':{'fields':['foto','descricao',],
            'mensagem':"Descreva ao máximo sua atividade para que o usuário \
             encontre as informações que procura. Note que este campo \
             será utilizado com página inicial de sua atividade. Você pode inserir imagens\
             links para outras páginas e até mesmo vídeos. Aproveite!" },

       '3':{'fields':['requer_inscricao','valor','instrucoes','msgonerror','tutorial','tutorial_url',
#                      'groups',
                      'permuta','num_max','espera','confirmacao','insc_mestra','insc_online',
                      'inicio_inscricao','termino_inscricao','inicio_confirmacao',
                      'termino_confirmacao','limitantes'],
            'mensagem':"Defina as estratégias de inscrições para esta atividade.\
                            Em caso de dúvidas consulte os balões dos campos." },

       '4':{'fields':['num_chamadas','certifica','frequencia_minima','certificados_impressos'],
            'mensagem':"Defina as condições para certificar um inscrito na atividade.\
                            Em caso de dúvidas consulte os balões dos campos." },

       '5':{'fields':['aceita_artigos',
#                      'avaliadores',
                      'ficha_avaliacao',
                      #'autores',
                      'num_artigos','num_artigos_grupo','vincular_grupo','num_autores',
                      'data_limite_submissao','dias_avaliacao','prazo_correcao','carta_aceite'],
            'mensagem':"Defina as condições para certificar um inscrito na atividade.\
                            Em caso de dúvidas consulte os balões dos campos." },  
}
                            
def ordem_inscricao(db,inscrito):
    n = 1 + db( (db.inscrito.atividade_id==inscrito.atividade_id ) & \
                (db.inscrito.fake==False) & (db.inscrito.id < inscrito.id) ).count()
    num_max = inscrito.atividade_id.num_max
    
    if num_max:
        if n > num_max:
            return u'%iº Lista de espera' %(n - num_max)
    return n


def frequencia_participacao(db,inscrito):
    """Retorna a frequencia de participacao individual do inscrito em questao"""
    atividade = inscrito.atividade_id
    pessoa = inscrito.pessoa_id
    n_listas = db(db.lista_presenca.atividade_id==atividade.id).count()
    n_presenca = db((db.lista_presenca_pessoas.pessoa_id==pessoa.id) & 
                    (db.lista_presenca_pessoas.lista_presenca_id==db.lista_presenca.id) &
                    (db.lista_presenca.atividade_id==atividade.id) ).count()

    return n_presenca*100./(n_listas or 1) #Previne que se divida por 0
    

def certifica_inscrito(db,inscrito):
    atividade = inscrito.atividade_id
    if atividade.min_frequen:
        freq = frequencia_participacao(db,inscrito)
        if freq>=float(atividade.min_frequen):
            return True
    
        else:
            return False
    
    else:
        return True


def pessoa_get_certificados(db,pessoa,atividade,inscrito=True,autor=True,organizacao=True):
    s = 1==1
    certificados = None
    if inscrito:
        inscritos = db((db.inscrito.pessoa_id==pessoa.id) & db.inscrito.atividade_id==atividade.id)._select(db.inscrito.id)
        s = s | ((db.certificado.table_name=='inscrito') & (db.certificado.object_id.belongs(inscritos)) )
        
        certificados = db(s).select() 
#    certificados = db((db.certificado.table=='inscrito'))    
#    inscrito_type = ContentType.objects.get_for_model(self)
#    certificados = Certificado.objects.filter(content_type=inscrito_type,object_id=self.id)

#        from portalPet.Organizacao.models import Lotacao,Organizacao,Divisao
#        lotacao_type = ContentType.objects.get_for_model(Lotacao)

#        #obtendo a organização da atividade
#        organizacao, created = Organizacao.objects.get_or_create(
#                content_type = ContentType.objects.get_for_model(Atividade),
#                object_id = self.atividade.id,
#        )
#        lotacoes = Lotacao.objects.filter(organizacao=organizacao,pessoa=self.pessoa)

#        if len(lotacoes):
#            lotacao_type = ContentType.objects.get_for_model(Lotacao)
#            certificados  = certificados | Certificado.objects.filter(content_type=lotacao_type,object_id=self.id)

#    autores_ids = Artigo.objects.filter(atividade=self.atividade).values_list('versao__autores',flat=True)
#    autores = Autor.objects.filter(Q(Q(pessoa=self.pessoa) | Q(nome=self.pessoa.nome)),id__in=autores_ids)
#    if autores.count():
#        autor_type = ContentType.objects.get_for_model(Autor)
#        certificados = certificados | Certificado.objects.filter(content_type=autor_type,object_id__in=autores.values_list('id',flat=True))

    return certificados


def num_inscritos_(db,atividade,confirmado=False,extra_query=None):
    """Retorna o número total de pessoas inscritas na atividade"""
    q = (db.inscrito.atividade_id==atividade.id) & (db.inscrito.fake==False)
    
    if confirmado and atividade.confirmacao:
        q = q & (db.inscrito.confirmado==True)
    
    if extra_query:
        q = q & extra_query
        
    return db(q).count()


def num_presenca(db,atividade):
    """Respresenta a média das pessoas que assinaram as listas"""
    listas = db((db.lista_presenca.atividade_id==atividade.id) & 
                (db.lista_presenca.finalizada==True) ).count()
    
    num_presencas = db((db.lista_presenca.atividade_id==atividade.id) & 
             (db.lista_presenca_pessoas.lista_presenca_id==db.lista_presenca.id)
        ).count()
    
    num_listas = db((db.lista_presenca.atividade_id==atividade.id)).count()
    
    n_inscritos = num_inscritos_(db,atividade,confirmado=True)
    
    if n_inscritos:
        return (num_presencas/(num_listas or 1) )*100./n_inscritos
        
    return num_presencas
    
    
def listas_feitas(db,atividade):
    if atividade.num_chamadas:
        n_listas = db((db.lista_presenca.atividade_id==atividade.id) & 
                      (db.lista_presenca.finalizada==True) ).count()
        
        return n_listas==int(atividade.num_chamadas)
    else:
        return True
        

def periodos_shortcut(db,atividade):
    periodos={}
    for p in db(db.atividade_periodo.atividade_id==atividade).select(orderby=db.atividade_periodo.inicio):
        inicio = p.inicio.date()
        termino = p.termino.date()
        if periodos.has_key(inicio):
            periodos[inicio]+=[p.inicio.time()]
        else:
            periodos[inicio]=[p.inicio.time()]
            
        if periodos.has_key(termino):
            periodos[termino]+=[p.termino.time()]
        else:
            periodos[termino]=[p.termino.time()]
            
    t='<table class="table table-bordered">'
    for data, horas in periodos.items():
        hrs=[]
        for i,h in enumerate(horas[::2]):
            hrs.append( ' - '.join(map(date2str,horas[i*2:2*(i+1)])) )
            
        n = len(hrs)
        t+='<tr><td rowspan="%s" style="vertical-align:middle;" align="center" class="col-xs-5"><b>%s</b></td> <td align="center" class="col-xs-7">%s</td> </tr>' %(n, date2str(data),hrs[0])
        for h in hrs[1:]:
            t+='<tr><td align="center">%s</td></tr>' %h
    
    t+='</table>'
#        t += date2str(date)

#        date2 = p.inicio.date()
#        if date==p.termino.date() and date2==date:
#            inicio = p.inicio.time()
#            termino = p.termino.time()
#            t+=" %s - %s" %(date2str(inicio),date2str(termino) )
#        else:
#            t+='<br/>'
#        date = p.inicio.date()
            
#    if np > 2:
#        periodos = [periodos[0],"...",periodos[np-1]]
    return XML(t)#''.join(['%s<br />' %db.atividade_periodo._format(periodo) for periodo in periodos or []]))
    

def atividade_inicio(db,atividade):
    min = db.atividade_periodo.inicio.min()
    return db(db.atividade_periodo.atividade_id==atividade.id).select(min).first()[min]


def atividade_termino(db,atividade):
    max = db.atividade_periodo.termino.max()
    return db(db.atividade_periodo.atividade_id==atividade.id).select(max).first()[max]



##----------------Congresso-----------------------------------------------------
def data_limite_avaliacao(db,atividade):
    atividade_congresso = db(db.atividade_congresso.atividade_id==atividade.id).select().first()
    if atividade_congresso:
        return (atividade_congresso.data_limite_submissao or atividade_inicio(atividade) + \
                timedelta(days=atividade_congresso.dias_avaliacao or 0) )
    else:
        return datetime.date.today()
            

def atividade_areas_conhecimento(db,atividade):
    areas_conhecimento = []
    for avaliador in db(db.avaliador.atividade_id==atividade.id).select():
        if avaliador.areas_conhecimento:
            areas_conhecimento += avaliador.areas_conhecimento
    areas_conhecimento = set(areas_conhecimento)
    return areas_conhecimento
        
        
def data_limite_submissao(db,atividade):
    atividade_congresso = db(db.atividade_congresso.atividade_id==atividade.id).select().first()
    return atividade_congresso.data_limite_submissao if atividade_congresso else None
         
         
def versao_dataRes(db,versao):
    artigo = versao.artigo_id
    atividade = artigo.atividade_id
    data_base = None
    if versao.avaliacao and versao.avaliacao.liberar:
        data_base = versao.avaliacao.data_avaliacao
    elif versao.revisao > 0:
        versao_anterior = db((db.versao.artigo_id==artigo.id) & (db.versao.revisao==versao.revisao - 1)).select().first()
        data_base = versao_anterior.avaliacao.data_avaliacao

    if data_base:
        return data_base + timedelta(days = atividade.prazo_correcao or 0)
    return data_limite_avaliacao(db,atividade)


def versao_editar(db,versao):
    if versao.avaliacao_id and versao.avaliacao_id.liberar:
        if versao.avaliacao_id.parecer=='am':
            if date.today() <= versao_dataRes(db,versao):
                return True

    elif date.today() <= (data_limite_submissao(db,versao.artigo_.atividade) or date.today() ):
        if not self.enviado:
            return True
            

def versao_status(db,versao,editar=None):
    avaliacao = versao.avaliacao_id
    if avaliacao and avaliacao.liberar:
        return db.avaliacao.parecer.represent(avaliacao,avaliacao.parecer)
        
    if editar or versao_editar(db,versao):
        if versao.revisao > 0:
            versaoAnterior = db((db.versao.artigo_id==artigo.id) & (db.versao.revisao==versao.revisao - 1)).select().first()
            return db.avaliacao.parecer.represent(versaoAnterior.avaliacao,versaoAnterior.avaliacao.parecer)
        return u'a enviar'
    return u'Sob Revisão'
    

def versao_prazo(db,versao,editar=None):
    """Retorna o prazo para o final da avaliação, ou prazo de correcao conforme o caso """
    if editar or versao_editar(db,versao):
        return versao_dataRes(db,versao)
    else:
        atividade = versao.artigo_id.atividade_id
        return data_limite_avaliacao(db,atividade)
            
            
def artigo_avaliacao_liberada(db,artigo,corrente=None):
    corrente = corrente if corrente else db(db.versao.artigo_id==artigo.id).select(orderby=~db.versao.revisao).first()
    if corrente:
        if corrente.revisao > 0 and (not corrente.avaliacao_id or \
                corrente.avaliacao_id and not corrente.avaliacao_id.liberar):
            
            versaoAnterior = db((db.versao.artigo_id==artigo.id) & (db.versao.revisao==versao.revisao - 1)).select().first()
            return versaoAnterior.avaliacao
        elif corrente.avaliacao_id and corrente.avaliacao_id.liberar:
            return corrente.avaliacao_id
