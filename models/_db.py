# -*- coding: utf-8 -*-
##IN PRODUCTION MODE:
from gluon.custom_import import track_changes; track_changes(True)
from gluon.debug import dbg
MIGRATE = True


##Public modules
import os
import uuid


##Personal Modules
from images import THUMB
from myutils import cooldate,date2str,datediff_T
from widgets import Autocomplete,bootstrap3,bootstrap_editor,datepicker,Fileinput
from custon_widgets import MultipleOptionsWidgetFK,SingleOptionsWidgetFK
from custon_helper import BREADCRUMB,Paginate


items_per_page=20
from django_login import django_login

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

db = DAL('sqlite://storage.db',
         migrate=MIGRATE,#fake_migrate=True,
         check_reserved=['postgres', 'mysql'],lazy_tables=True)


## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []

## (optional) optimize handling of static files
#response.optimize_css = 'concat,minify,inline'
#response.optimize_js = 'concat,minify,inline'

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db)
crud, service, plugins = Crud(db), Service(), PluginManager()

crud.settings.formstyle = auth.settings.formstyle = bootstrap3
auth.settings.hmac_key = 'pbkdf2(10000,20,sha256):vbv+xrner#*#y-ug(hb4b9$_zt5+-nt+84*)*-5s*r+jjd231j'

auth.settings.extra_fields['auth_user']= [
  Field('original_id','integer',writable=False,readable=False),
  Field('username_','string'),
  Field('date_joined','datetime'),
  Field('django_password','string')
]


## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)


auth.settings.login_methods.append(django_login(db) )



## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' or 'smtp.gmail.com:587'
mail.settings.sender = 'you@gmail.com'
mail.settings.login = 'username:password'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

auth.settings.login_next = auth.settings.profile_next =  URL('default','pessoa')
auth.settings.expiration = 3600*2

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
from gluon.contrib.login_methods.rpx_account import use_janrain
use_janrain(auth, filename='private/janrain.key')


##----------------Only in production--------------------------------------------
db._common_fields.append( Field('original_id','integer',readable=False,writable=False) )

##------------------------------------------------------------------------------


def format_cidade(r):
    try:
        if isinstance(r, (int, long)):
            r = db.cidade[r]
        return "%s - %s" %(r.nome,r.estado_id.sgl) if r else ""
    except:
        return r
    
db.define_table('cidade',
    Field('nome','string',notnull=True),
    Field('estado_id','reference estado',notnull=True),
    format = format_cidade,
    migrate=MIGRATE)


db.define_table('estado',
    Field('nome','string',notnull=True),
    Field('sgl','string',notnull=True),
    format="%(nome)s - %(sgl)s",
    migrate=MIGRATE)
    

db.define_table('tema',
    Field('nome','string'),
    Field('descricao','string'),
    Field('ativo','integer'),
    migrate=MIGRATE)
    
    
db.define_table('pessoa',
    Field('nome','string',required=True),
    Field('cidade_id','reference cidade',label='Cidade',
          widget=Autocomplete(URL('default','get_cidade',extension='json'),format=db.cidade._format).widget,
          requires=IS_EMPTY_OR(IS_IN_DB(db,'cidade.id',label=lambda r: db.cidade._format(r))), 
          represent=lambda c,r: db.cidade._format(db.cidade[c]) ),
    Field('foto','upload',widget=Fileinput(image=True).widget,
          uploadfolder=os.path.join(request.folder,'uploads','users','photos') ),
    Field('slug','string',compute=lambda r: IS_SLUG()(r['nome'])[0],readable=False ),
    Field('tema_id','reference tema',writable=False,readable=False,requires=None,notnull=False),
    Field('miniatura','upload',uploadfolder=os.path.join(request.folder,'uploads','users','photos'),
          compute=lambda row: THUMB(row.foto,folder=['uploads','users','photos']) ),

    format="%(nome)s",
    migrate=MIGRATE
)

db.pessoa._after_update.append(lambda s,f: \
    s.update_naive(miniatura=db.pessoa.miniatura.compute(s.select().first()) ) )

db.define_table('pessoa_fisica',
    Field('user_id','reference auth_user',readable=False,writable=False),
    Field('pessoa_id','reference pessoa',readable=False,writable=False,
          label="Pessoa",
          widget=SingleOptionsWidgetFK(
            response,
            url_args=['default','pessoa'],
            url_kwargs=dict(args=('criar',))).widget
    ),
    Field('sobremim','text',comment="Escreva algo sobre você"),
    Field('apelido','string'),
    Field('rede_social','list:string'),
    Field('rg','string',label="RG:"),
    Field('cpf','string',label="CPF:"),
    Field('sexo','string',requires=IS_IN_SET([('M','Masculino'),('F','Feminino')])),
    Field('data_nascimento','date',represent=lambda d,r: date2str(d),widget=datepicker ),
    Field('ra','string'),
    Field('curso','string'),
    Field('cidade_estudo_id','reference cidade',label="Cidade Estudo",
          widget = Autocomplete(URL('default','get_cidade',extension='json')).widget,
          represent=lambda c,r: db.cidade._format(db.cidade[c]) ),
    Field('website','string',requires=IS_EMPTY_OR(IS_URL()) ),
    
    format=lambda r: r.pessoa_id.nome,
    migrate=MIGRATE)


#Antiga tabela Entidade!
db.define_table('pessoa_juridica',
    Field('pessoa_id','reference pessoa'),
    Field('cnpj','string',length=20),
    Field('inscricao_estadual','string',length=20),
    Field('inscricao_municipal','string',length=20),
    Field('telefone','string',length=100),
    Field('cep','string',length=9),
    Field('endereco','string',length=200),
    Field('complemento','string',length=200),
    Field('sitio','string',length=200,requires=IS_EMPTY_OR(IS_URL())),
    format = lambda r: r.pessoa_id.nome if r else "",
    migrate=MIGRATE)


#Antiga tabela contato_pessoa
db.define_table('pessoa_contato',
    Field('pessoa_id','reference pessoa_fisica',label="Pessoa"),
    Field('instituicao_id','reference pessoa_juridica',label="Instituição"),
    Field('especialidades','list:string'),
    Field('telefone','string',length=100),
    Field('observacao','text',label=u"Observação"),
    format = lambda r: r.pessoa_id.nome,
    migrate=MIGRATE)


def readed_message(row):
    pessoa_ = db((db.pessoa_fisica.pessoa_id==db.pessoa.id) & \
                (db.pessoa_fisica.user_id==auth.user_id)).select(db.pessoa_fisica.pessoa_id).first()
    if pessoa_:
        dst = db((db.mensagem_readers.mensagem_id==row.mensagem.id) & \
                 (db.mensagem_readers.pessoa_id==pessoa_.pessoa_id)).count()
        return dst or row.mensagem.de==pessoa_.pessoa_id

def render_resposta(row,can_del):
    pessoa_ = db((db.pessoa_fisica.pessoa_id==db.pessoa.id) & \
                (db.pessoa_fisica.user_id==auth.user_id)).select().first()
    if pessoa_:
        q1 = (db.mensagem.resposta==row.mensagem.id) & (db.mensagem.id!=row.mensagem.id) #resposta
        q2 = (db.mensagem.id==db.mensagem_destinatarios.mensagem_id) & \
             (db.mensagem_destinatarios.pessoa_id==pessoa_.pessoa.id) #Se é destinatario
        q3 = db.mensagem.de==_pessoa.pessoa.id ##se é autor da mensagem
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

db.define_table('mensagem',
    Field('master','reference mensagem',readable=False,writable=False),
    Field('de','reference pessoa'),
    Field('assunto','string',requires=IS_NOT_EMPTY(),required=True ),
    Field('hora','datetime',default=request.now,writable=False,readable=False,represent=lambda d,r: date2str(d)),
    Field('conteudo','text',widget=bootstrap_editor,requires=IS_NOT_EMPTY(),required=True),
    Field('hash','string',readable=False,writable=False,length=64, default=lambda:str(uuid.uuid4())),
    Field.Method('readed',readed_message),
    Field.Method('render_resposta',render_resposta),
    format = "%(assunto)s",
    migrate=MIGRATE)

#db.mensagem._after_insert.append(lambda f,id: create_hash(db,'mensagem',id))


db.define_table('mensagem_destinatarios',
    Field('mensagem_id','reference mensagem',readable=False,writable=False),
    Field('pessoa_id','reference pessoa',readable=False,writable=False),
    format = lambda r: "%s - %s" %(r.mensagem_id.assunto,r.pessoa_id.nome),
    migrate=MIGRATE)


db.define_table('mensagem_readers',
    Field('mensagem_id','reference mensagem',readable=False,writable=False),
    Field('pessoa_id','reference pessoa',readable=False,writable=False),
    format = lambda r: "%s - %s" %(r.mensagem_id.assunto,r.pessoa_id.nome),
    migrate=MIGRATE)


db.define_table('peoplegroup',
    Field('nome','string'),
    migrate=MIGRATE)


db.define_table('peoplegroup_pessoas',
    Field('peoplegroup_id','integer'),
    Field('pessoa_id','integer'),
    migrate=MIGRATE)


#db.define_table('Balanco_balanco',
#    migrate=MIGRATE)


#db.define_table('Balanco_balanco_despesas',
#    Field('balanco_id','integer'),
#    Field('despesa_id','integer'),
#    migrate=MIGRATE)


#db.define_table('Balanco_balanco_receitas',
#    Field('balanco_id','integer'),
#    Field('receita_id','integer'),
#    migrate=MIGRATE)


#db.define_table('Balanco_despesa',
#    Field('descricao','string'),
#    Field('natureza','string'),
#    Field('valor','double'),
#    Field('data','date'),
#    migrate=MIGRATE)


#db.define_table('Balanco_receita',
#    Field('descricao_id','integer'),
#    Field('natureza','string'),
#    Field('valor','double'),
#    Field('data','date'),
#    Field('vinculo','string'),
#    migrate=MIGRATE)


db.define_table('custompermission',
    Field('codename','string'),
    Field('content_type_id','integer'),
    Field('object_id','integer'),
    Field('creator_id','integer'),
    migrate=MIGRATE)


db.define_table('custompermission_groups',
    Field('custompermission_id','integer'),
    Field('grupousergroup_id','integer'),
    migrate=MIGRATE)


db.define_table('custompermission_users',
    Field('custompermission_id','integer'),
    Field('user_id','integer'),
    migrate=MIGRATE)


db.define_table('grupousergroup',
    Field('group_ptr_id','integer'),
    Field('nome','string'),
    migrate=MIGRATE)


#db.define_table('tema',
#    Field('layout_base_id','integer'),
#    Field('layout_menu_id','integer'),
#    Field('layout_formulario_id','integer'),
#    Field('layout_tabela_id','integer'),
#    migrate=MIGRATE)


#db.define_table('configuracao',
#    Field('layout_id','reference layout'),
#    Field('permissions_id','integer'),
#    migrate=MIGRATE)


db.define_table('pendedform',
#    Field('db_name','string'),
    Field('table_name','string'),
    Field('hash','string',required=True,readable=False,writable=False,length=64, default=lambda:str(uuid.uuid4())),
    Field('instance_id','integer'),
    migrate=MIGRATE)


db.define_table('pendedvalue',
    Field('form_id','reference pendedform'),
    Field('field_name','string'),
    Field('field_value','text'),
    migrate=MIGRATE)


#db.define_table('balanco',
#    migrate=MIGRATE)


#db.define_table('balanco_despesas',
#    Field('balanco_id','integer'),
#    Field('despesa_id','integer'),
#    migrate=MIGRATE)


#db.define_table('balanco_receitas',
#    Field('balanco_id','integer'),
#    Field('receita_id','integer'),
#    migrate=MIGRATE)


db.define_table('despesa',
    Field('descricao','string'),
    Field('natureza','string'),
    Field('valor','double'),
    Field('data','date'),
    migrate=MIGRATE)


db.define_table('convenio',
    Field('table_name','string',required=True,requires=IS_IN_SET(('grupo',)) ),
    Field('object_id','integer',required=True),
    Field('agencia','string',length=15,required=True),
    Field('conta','string',length=20,required=True),
    Field('banco','string',length="2",requires=IS_IN_SET([('bb','Banco do Brasil')],),default="bb" ),
    Field('cedente','string',comment=u"Razão social ou nome fantasia da empresa. Nome do titular da conta"),
    Field('convenio','string',comment=u"Muito cuidado com este número pois um digito errado irá implicar no não recebimento do valor pago!!"),
    Field('carteira','string',requires=IS_IN_SET(('18',)),comment=u"Número que deve ser obtido no banco. Este número varia de acordo com a modalidade de cobrança escolhida" ),
    migrate=MIGRATE)
    
    
db.define_table('boleto',
    Field('convenio_id','reference convenio',required=True),
    Field('nosso_numero','integer',required=True),
    Field('numero_documento','string',required=True),
    Field('pessoa_id','reference pessoa'),
    Field('valor','double',required=True),
    Field('valor_pago','double'),
    Field('vencimento','date'),
    Field('sinalizar_pago','boolean'),
    Field('trash','boolean'),
    common_filter = lambda query: db.boleto.trash==False,
    migrate=MIGRATE)


##Relaciona quais objetos compoe o boleto
db.define_table('boleto_objeto',
    Field('boleto_id','reference boleto'),
    Field('table_name','string',required=True),
    Field('object_id','integer',required=True),
    migrate=MIGRATE)
    
    
db.define_table('receita',
    Field('descricao','string'),
    Field('patrocinador_id','integer'),
    Field('natureza','string'),
    Field('valor','double'),
    Field('data','date'),
    Field('vinculo','string'),
    migrate=MIGRATE)


db.define_table('grupo',
    Field('nome','string',comment="Insira o nome do Grupo"),
    Field('data_fundacao','date',comment="Data em que seu grupo foi criado"),
    Field('historico','text',widget=bootstrap_editor,comment="Insira informações a respeito do seu grupo"),
    Field('cidade_id','reference cidade',label="Cidade",
          widget=Autocomplete(URL('default','get_cidade',extension='json'),format=db.cidade._format).widget,
          requires=IS_EMPTY_OR(IS_IN_DB(db,'cidade.id')), 
          represent=lambda c,r: db.cidade._format(db.cidade[c]),
          comment="A cidade onde seu grupo está instalado" ),
    Field('curso','string'),
    Field('instituicao_id','reference pessoa_juridica',label="Instituição",
            requires=IS_EMPTY_OR(IS_IN_DB(db,'pessoa_juridica.id')),
            represent=lambda i,r: db.pessoa_juridica._format(db.pessoa_juridica[i]) ),
#    Field('tutor_id','integer',label="Tutor"),
    Field('slug','string',readable=False,writable=False,
          compute=lambda r: IS_SLUG()("%s %s" %(r['nome'], db.cidade._format(db.cidade[r['cidade_id']])) )[0] ),
    Field('foto','upload',
            uploadfolder=os.path.join(request.folder,'uploads','grupos','photos') ),
    Field('miniatura','upload',uploadfolder=os.path.join(request.folder,'uploads','grupos','photos'),
          compute=lambda row: THUMB(row.foto,folder=['uploads','grupos','photos']) ),
    Field('ativo','integer',readable=False,writable=False),
    Field('configuracao_id','integer',readable=False,writable=False),
    Field('email','string'),
    Field('pessoa_id','reference pessoa',readable=False,writable=False,
            requires=IS_EMPTY_OR(IS_IN_DB(db,'pessoa.id')),unique=True ),
    Field('twitter','string'),
    Field.Method('get_related',lambda row,table:\
            db(db[table]['grupo_id']==row.grupo.id) ),
    format = lambda r: "%s - %s" %(r['nome'],db.cidade._format(db.cidade[r['cidade_id']]) ),
    migrate=MIGRATE)


db.define_table('integrante',
    Field('pessoa_id','reference pessoa',required=True,readable=False,writable=False),
    Field('grupo_id','reference grupo',required=True,readable=False,writable=False),
    Field('tipo','string',required=True,
            requires=IS_IN_SET(dict(i='Integrante',ie='Integrante Egresso',
                                    t='Tutor',te='Tutor Egresso')) ),
    Field('nasc','date'),
    Field('endereco','string'),
    Field('orkut','string'),
    Field('lattes','string'),
    Field('ing_Facu','date'),
    Field('ing_Pet','date'),
    Field('ing_Bolsa','date'),
    Field('saida_Bolsa','date'),
    Field('saida_Pet','date'),
    format=lambda r: r.pessoa_id,
    migrate=MIGRATE)


atividade_tipos = {'ev':u'Evento','pa':u'Palestra','se':u'Seminário',
                   'cu':u'Curso','vi':u'Viagem','ps':u'Pesquisa','cd':u'Credenciamento',
                   'ou':u"Outro"}
atividade_classificacao = {'en':u'Ensino','ps':u'Pesquisa','ex':u'Extensão',
                           'tr':u'Ensino, Pesquisa e Extensao','ot':u'Outros'}
db.define_table('atividade',
    Field('grupo_id','reference grupo',required=True,writable=False,readable=False),
    Field('nome','string',required=True),
    Field('tipo','string',required=True,
          represent=lambda v,r: atividade_tipos[v],
          requires=IS_IN_SET(atividade_tipos) ),
    Field('classificacao','string',label=u'Classificação',
          represent=lambda v,r: atividade_classificacao[v],
          requires=IS_IN_SET(atividade_classificacao) ),
#    Field('contato_id','integer'),
    Field('obs','string'),
    Field('descricao','text',label="Descrição",comment="Insira o máximo de informações relativas a esta atividade. Este campo se transfomará na página inicial do perfil desta atividade.",widget=bootstrap_editor),
    Field('foto','upload',uploadfolder=os.path.join(request.folder,'uploads','atividades','photos') ),
    Field('miniatura','upload',uploadfolder=os.path.join(request.folder,'uploads','atividades','photos'),
          compute=lambda row: THUMB(row.foto,nx=200,ny=200,folder=['uploads','atividades','photos']) ),
    Field('certifica','boolean',label=u'Libera Certificado',comment=u"Marque este campo para indicar que esta atividade fornecerá certificados para os participantes que obtiverem a frequencia mínima"),
    Field('frequencia_minima','double',label='Frequência minima (%)',comment=u'Valor que representa a menor porcentagem de presença que o participante deve ter para receber o certificado. Caso não seja exigida uma frequência mínima deixe este campo em branco.'),
    Field('certificados_impressos','boolean',label='Certificado Liberado',comment=u"Marque este campo para informar que os certificados estão prontos. Além de aparecer uma mensagem na página inicial do evento informando que os certificados estão prontos os certificados só ficarão disponíveis na página do usuário se este campo estiver marcado."),
    Field('mini_relatorio','boolean',label="Mini relatório",comment=u"Marque este campo para informar que esta atividade requer mini-relatório"),
    Field('requer_inscricao','boolean',label="Requer Inscricao",comment=u"Marque este campo para indicar que os participantes devem se inscrever nesta atividade."),
    Field('instrucoes','text',label=u'Instruções',comment="Utilize este campo para passar as instruções relativas as inscrições aos usuários do portal",widget=bootstrap_editor),
    Field('msgonerror','text',comment=u"Utilize este campo para passar informações para que os usuários que estão encontrando dificuldade em se inscrever consigam resolver.",widget=bootstrap_editor),
    Field('tutorial','text',comment=u"Faça um breve tutorial de inscrição.",widget=bootstrap_editor),
    Field('tutorial_url','string',comment="Informe a url do tutorial. Note que se o campo anterior for preenxido apenas seu conteudo será apresentado",length=400),
    Field('insc_mestra','boolean',label='Requer a inscrição na Mestra',comment="Marque este campo para informar que para o participante se inscrever nesta atividade ele deve antes de se inscrito no evento correspondente."),
    Field('insc_online','boolean',label='Libera inscricao on-line',comment="Marque este campo para que os participantes possam se inscrever on-line."),
    Field('espera','boolean',label='Libera lista de espera',comment="Marque este campo para que as pessoas continuem se inscrevendo mesmo que o número máximo de inscritos seja alcançado. Observe que seus nomes ficam em uma lista de espera aguardando possíveis vagas."),
    Field('permuta','boolean',comment="Quando marcado permite que haja troca de inscrições até a data limite de inscrição"),
    Field('inicio_inscricao','date',label='Início Inscrição',comment="Data a partir da qual as inscrições serão liberadas. Note que se deixado em branco a inscrição estará disponível de imediato."),
    Field('termino_inscricao','date',label='Término Inscrição',comment="Data a partir da qual as inscrições serão encerradas. Note que, se deixado em branco as inscrições se encerrarão quando a atividade se iniciar."),
    Field('num_max','integer',label='Número máximo de Inscritos',comment="Número máximo de pessoas que podem participar desta atividade. Note que para o caso de eventos este número avaliará apenas as pessoas inscritas no evento, não levando em consideração as inscritas nas sub-atividades. Se deixado em branco 'infinitas' pessoas poderão se inscrever."),
    Field('valor','double',label='Valor da Inscricao'),
    Field('confirmacao','boolean',label='Requer Confirmação',comment='Quando marcado indica que o inscrito deverá confirmar que irá participar desta atividade até a data que você especificar. A confirmação é uma medida que visa evitar que as pessoas se inscrevam e se esqueçam de participar da atividade.'),
    Field('inicio_confirmacao','date',label='Início Confirmação',comment="Data a partir da qual se iniciará o período de confirmação. Uma boa prática é que esta data se inicie logo após o encerramento das inscrições para que os inscritos possam confirmar a presença na atividade. Note que se deixado em branco a confirmação estará disponível ao término das inscrições. "),
    Field('termino_confirmacao','date',label='Término Confirmação',comment="Data a partir da qual o período de confirmação se encerra. Quando utilizado em paralelo a lista de espera, é uma boa prática que esta data seja um ou dois dias antes do início da atividade, este tempo serve para as pessoas se informaram a respeito de sua vaga. Note que se deixado em branco a confirmação vai até o inicio da atividade."),
    Field('limitantes','list:string',label='Combinações possíveis',comment='Este campo serve para limitar o número de atividades que uma pessoa pode se inscrever em um evento. Informe em cada linha da tabela uma combinação possível. Por exemplo, para limitar a uma palestra e 1 curso digite "um" em palestra e em curso na primeira linha, e caso existam outras opções, insira novas linhas com suas respectivas combinações.'),
    Field('num_chamadas','integer',label='Número de listas de presença',comment='Estimativa do número de vezes que se passará a lista de presença durante a atividades.'),
#    Field('balanco_id','integer'),
#    Field('configuracao_id','integer'),
    Field('divulgar','boolean',comment="Quando marcado, todos poderão ver esta atividade."),
    Field('slug','string',compute=lambda r: IS_SLUG()(r.nome)[0] ),
    format = "%(nome)s",
    migrate=MIGRATE)


db.define_table('atividade_periodo',
    Field('atividade_id','reference atividade',required=True),
    Field('inicio','datetime',required=True),
    Field('termino','datetime',required=True),
    format=lambda r: "%s %s" %(date2str(r.inicio),date2str(r.termino) ) ,
    migrate=MIGRATE)


db.define_table('divisao',
    Field('grupo_id','integer'),
    Field('nome','string'),
    migrate=MIGRATE)


db.define_table('lotacao',
    Field('divisao_id','integer'),
    Field('organizacao_id','integer'),
    Field('pessoa_id','reference pessoa'),
    migrate=MIGRATE)


db.define_table('organizacao',
    Field('content_type_id','integer'),
    Field('object_id','integer'),
    Field('descricao','text'),
    Field('data_ini','date'),
    Field('data_ter','date'),
    migrate=MIGRATE)


db.define_table('acao',
    Field('table_name','string'),
    Field('object_id','integer'),
    Field('estado','string',requires=IS_IN_SET({'p':'Ação Pendente','r':'Processando','c':'Ação Concluido'}),default="p"),
    Field('error','boolean'),
    Field('errorinfo','text'),
    migrate=MIGRATE)


db.define_table('acao_grupo',
    Field('titulo','string'),
    Field('data_solicitacao','datetime'),
    Field('data_processamento','datetime'),
    Field('showed','datetime'),
    Field('estado','string',requires=IS_IN_SET([('p','Ação Pendente'),('r','Processando'),('c','Ação Concluido')]),default="p"),
    Field('comentario','text'),
    Field('user_id','reference auth_user'),
    migrate=MIGRATE)


db.define_table('acao_grupo_acoes',
    Field('acao_grupo_id','integer'),
    Field('acao_id','integer'),
    migrate=MIGRATE)


db.define_table('arquivo',
    Field('nome','string',required=True),
    Field('keyword','list:string'),
    Field('tipo','string',requires=IS_IN_SET(
        {'1':'Arquivo','2':'Apostila','3':'Documento','4':'Foto','5':'Memorando',
         '6':'Mini-Relatório','7':'Relatório','8':'Requerimento','9':'Ata eletrônica'}) ),
    Field('data','date',default=request.now),
    Field('arquivo','upload',),
    Field('comentario','text'),
    format="%(nome)s",
    migrate=MIGRATE)


db.define_table('arquivotemporario',
    Field('arquivo','string'),
    migrate=MIGRATE)


db.define_table('desenvolvedor',
    Field('pessoa_id','reference pessoa'),
    Field('func','string'),
    Field('inicio','date'),
    Field('ativo','integer'),
    migrate=MIGRATE)


db.define_table('mailmessage',
    Field('subject'),
    Field('message','text',required=True),
    Field('mail_to',required=True,requires=IS_EMAIL()),
    Field('reply_to',requires=IS_EMPTY_OR(IS_EMAIL()),default=mail.settings.sender),
    Field('attachments','list:reference arquivo'),
    Field('sended','boolean'),
    Field('data_pedido','date',default=request.now),
    Field('data_envio','date'),
    migrate=MIGRATE)


db.define_table('portal',
    Field('tema_id','integer'),
    migrate=MIGRATE)


db.define_table('portal_desenvolvedores',
    Field('portal_id','integer'),
    Field('desenvolvedor_id','integer'),
    migrate=MIGRATE)


db.define_table('sugestao',
    Field('pessoa_id','reference pessoa'),
    Field('pagina','string'),
    Field('descricao','text'),
    Field('prioridade','integer'),
    Field('status','integer'),
    Field('resumo','string'),
    migrate=MIGRATE)


db.define_table('sugestao_desenvolvedores',
    Field('sugestao_id','integer'),
    Field('desenvolvedor_id','integer'),
    migrate=MIGRATE)


db.define_table('admin_tools_dashboard_preferences',
    Field('user_id','integer'),
    Field('data','text'),
    Field('dashboard_id','string'),
    migrate=MIGRATE)


db.define_table('django_flatpage',
    Field('url','string'),
    Field('title','string'),
    Field('content','text'),
    Field('enable_comments','integer'),
    Field('template_name','string'),
    Field('registration_required','integer'),
    migrate=MIGRATE)


db.define_table('facebookprofile',
    Field('user_id','integer'),
    Field('facebook_id','integer'),
    Field('access_token','string'),
    migrate=MIGRATE)


db.pessoa.cidade_id.requires = db.pessoa_fisica.cidade_estudo_id.requires = \
            IS_EMPTY_OR(IS_IN_DB(db, 'cidade.id', '%(nome)s'))

db.pessoa.cidade_id.represent = db.pessoa_fisica.cidade_estudo_id.represent = db.cidade._format


#for r in db((db.mensagem.hash==None) | (db.mensagem.hash=='')).select():
#    create_hash(db,'mensagem',r.id)

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

from pessoa_utils import get_pessoa
global unreaded

#from gluon.tools import prettydate

SQLFORM.formstyles.table3cols = bootstrap3
pessoa = get_pessoa(request,db,auth,force_auth=True)

unreaded = None
if pessoa:
    unreaded = db((db.mensagem_destinatarios.pessoa_id==pessoa.pessoa.id) &
                      (db.mensagem.id==db.mensagem_destinatarios.mensagem_id) ).count(distinct=True) - \
                   db((db.mensagem_readers.mensagem_id==db.mensagem.id) & \
                      (db.mensagem_readers.pessoa_id==pessoa.pessoa.id) &
                     ~(db.mensagem.de==pessoa.pessoa.id)).count(distinct=True,cache=(cache.ram, 60))




#for t in db._tables:
#    print t
#    a=db(db[t].id>0).select(limitby=(0,1))
