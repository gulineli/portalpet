# -*- coding: utf-8 -*-

# IN PRODUCTION MODE:
from gluon.custom_import import track_changes; track_changes(True)


# Public modules
import os
import uuid


# web2py modules
from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
from gluon import current

# Personal Modules
import db_utils
import server
from images import THUMB
from myutils import cooldate, date2str, datediff_T
from widgets import Autocomplete, bootstrap3, bootstrap_editor, datepicker, Fileinput
from custon_widgets import MultipleOptionsWidgetFK, SingleOptionsWidgetFK
from custon_helper import BREADCRUMB
from html_utils import Paginate
from general_utils import truncate_words

items_per_page = 20
from django_login import django_login


RWF = dict(readable=False, writable=False)


db = DAL(server.SIGNATURE,
         migrate=False, #server.MIGRATE,
         # fake_migrate=True,
         check_reserved=['postgres', 'mysql'],
         lazy_tables=True
         )


response.generic_patterns = ['*'] if request.is_local else []


auth = Auth(db)
crud, service, plugins = Crud(db), Service(), PluginManager()

crud.settings.formstyle = auth.settings.formstyle = bootstrap3
auth.settings.hmac_key = server.HMAC_KEY


# Adiciona as colunas personalizadas para o auth_user padrão do web2py
auth.settings.extra_fields['auth_user']= [
  Field('original_id', 'integer', **RWF),
  Field('username_', 'string'),
  Field('username', 'string'),
  Field('date_joined', 'datetime'),
  Field('django_password', 'string')
]

# Adiciona as colunas personalizadas para o auth_group padrão do web2py
auth.settings.extra_fields['auth_group'] = [Field('full_description')]

# Define as tabelas do auth
auth.define_tables(username=True, signature=False)

# Remove as verificações do campo de email para permitir que o usuário possa
# se logar utilizando o usuário ou email
db.auth_user.email.requires = []

# Permite que usuários do portalpet antigo possa se logar com suas senhas antigas
auth.settings.login_methods.append(django_login(db))

#  Configurações de email
mail = auth.settings.mailer
mail.settings.server = 'logging' or 'smtp.gmail.com:587'
mail.settings.sender = 'you@gmail.com'
mail.settings.login = 'username:password'

#  Configurações da politica de registro
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True


auth.settings.login_next = URL('default', 'pessoa')
#auth.settings.profile_next = URL('default', 'pessoa')
auth.settings.expiration = 3600*2
#auth.settings.login_onfail = URL('ggg')

current.auth = auth

db._common_fields.append( Field('original_id', 'integer'))


db.define_table('cidade',
    Field('nome', 'string', notnull=True),
    Field('estado_id', 'reference estado', notnull=True),
    format=lambda row: db_utils.cidade_format(db, row)
)


db.define_table('estado',
    Field('nome', 'string', notnull=True),
    Field('sgl', 'string', notnull=True),
    format=lambda row: db_utils.estado_format(db, row),
)


db.define_table('tema',
    Field('nome', 'string'),
    Field('descricao', 'string'),
    Field('ativo', 'boolean'),
)


db.define_table('pessoa',
    Field('nome', 'string', required=True),
    Field('cidade_id', 'reference cidade', label='Cidade',
          widget=Autocomplete(URL('default', 'get_cidade', extension='json'),
                              format=db.cidade._format).widget,
          requires=IS_EMPTY_OR(IS_IN_DB(db, 'cidade.id',
                                        label=lambda r: db.cidade._format(r))),
          represent=lambda c, r: db.cidade._format(db.cidade[c])),
    Field('foto', 'upload', widget=Fileinput(image=True).widget,
          uploadfolder=os.path.join(request.folder, 'uploads', 'users', 'photos') ),
    Field('slug', 'string', compute=lambda r: IS_SLUG()(r['nome'])[0], readable=False ),
    Field('tema_id', 'reference tema', requires=None, notnull=False, **RWF),
    Field('miniatura', 'upload',
          uploadfolder=os.path.join(request.folder, 'uploads', 'users', 'photos'),
          compute=lambda row: THUMB(row.foto,folder=['uploads', 'users', 'photos'])),
    format="%(nome)s",
)


db.define_table('pessoa_fisica',
    Field('user_id', 'reference auth_user', **RWF),
    Field('pessoa_id', 'reference pessoa',label="Pessoa",
          widget=SingleOptionsWidgetFK(
            response,
            url_args=['default', 'pessoa'],
            url_kwargs=dict(args=('criar',))).widget,
          **RWF
    ),
    Field('sobremim', 'text', comment="Escreva algo sobre você"),
    Field('apelido', 'string'),
    Field('rede_social', 'list:string'),
    Field('rg', 'string', label="RG:"),
    Field('cpf', 'string', label="CPF:"),
    Field('sexo', 'string', requires=IS_IN_SET([('M', 'Masculino'),('F', 'Feminino')])),
    Field('data_nascimento', 'date', widget=datepicker ),
    Field('ra', 'string'),
    Field('curso', 'string'),
    Field('cidade_estudo_id', 'reference cidade', label="Onde Estudo",
          widget = Autocomplete(URL('default', 'get_cidade', extension='json')).widget),
    Field('website', 'string', requires=IS_EMPTY_OR(IS_URL()) ),

    format=lambda r: r.pessoa_id.nome,
)


# Antiga tabela Entidade!
db.define_table('pessoa_juridica',
    Field('pessoa_id', 'reference pessoa'),
    Field('cnpj', 'string', length=20),
    Field('inscricao_estadual', 'string', length=20),
    Field('inscricao_municipal', 'string', length=20),
    Field('telefone', 'string', length=100),
    Field('cep', 'string', length=9),
    Field('endereco', 'string', length=200),
    Field('complemento', 'string', length=200),
    Field('sitio', 'string', length=200, requires=IS_EMPTY_OR(IS_URL())),
    format = lambda r: r.pessoa_id.nome if r else "",
)


# Antiga tabela contato_pessoa
db.define_table('pessoa_contato',
    Field('pessoa_id', 'reference pessoa_fisica', label="Pessoa"),
    Field('instituicao_id', 'reference pessoa_juridica', label="Instituição"),
    Field('especialidades', 'list:string'),
    Field('telefone', 'string', length=100),
    Field('observacao', 'text', label=u"Observação"),
    format = lambda r: r.pessoa_id.nome,
)


db.define_table('mensagem',
    Field('master', 'reference mensagem', **RWF),
    Field('de', 'reference pessoa'),
    Field('assunto', 'string', requires=IS_NOT_EMPTY(), required=True ),
    Field('hora', 'datetime', default=request.now, **RWF),
    Field('conteudo', 'text', widget=bootstrap_editor,
          requires=IS_NOT_EMPTY(), required=True),
    Field('hash', 'string', length=64,
          readable=False, writable=False,
          default=lambda:str(uuid.uuid4())),
    Field.Lazy('is_read', lambda row: db_utils.mensagem_is_read(db, row)),
    Field.Method('render_resposta',
                 lambda row, can_del: mensagem_render_resposta(db, row, can_del)),

    format = "%(assunto)s",
)


db.define_table('mensagem_destinatarios',
    Field('mensagem_id', 'reference mensagem', **RWF),
    Field('pessoa_id', 'reference pessoa', **RWF),

    format = lambda r: "%s - %s" %(r.mensagem_id.assunto, r.pessoa_id.nome),
)


db.define_table('mensagem_readers',
    Field('mensagem_id', 'reference mensagem', required=True),
    Field('pessoa_id', 'reference pessoa', required=True),
)


db.define_table('peoplegroup',
    Field('nome', 'string'),
)


db.define_table('peoplegroup_pessoas',
    Field('peoplegroup_id', 'integer'),
    Field('pessoa_id', 'integer'),
)


#db.define_table('Balanco_balanco',
#)


#db.define_table('Balanco_balanco_despesas',
#    Field('balanco_id', 'integer'),
#    Field('despesa_id', 'integer'),
#)


#db.define_table('Balanco_balanco_receitas',
#    Field('balanco_id', 'integer'),
#    Field('receita_id', 'integer'),
#)


#db.define_table('Balanco_despesa',
#    Field('descricao', 'string'),
#    Field('natureza', 'string'),
#    Field('valor', 'double'),
#    Field('data', 'date'),
#)


#db.define_table('Balanco_receita',
#    Field('descricao_id', 'integer'),
#    Field('natureza', 'string'),
#    Field('valor', 'double'),
#    Field('data', 'date'),
#    Field('vinculo', 'string'),
#)


db.define_table('custompermission',
    Field('codename', 'string'),
    Field('content_type_id', 'integer'),
    Field('object_id', 'integer'),
    Field('creator_id', 'integer'),
)


db.define_table('custompermission_groups',
    Field('custompermission_id', 'integer'),
    Field('grupousergroup_id', 'integer'),
)


db.define_table('custompermission_users',
    Field('custompermission_id', 'integer'),
    Field('user_id', 'integer'),
)


db.define_table('grupousergroup',
    Field('group_ptr_id', 'integer'),
    Field('nome', 'string'),
)


#db.define_table('tema',
#    Field('layout_base_id', 'integer'),
#    Field('layout_menu_id', 'integer'),
#    Field('layout_formulario_id', 'integer'),
#    Field('layout_tabela_id', 'integer'),
#)


#db.define_table('configuracao',
#    Field('layout_id', 'reference layout'),
#    Field('permissions_id', 'integer'),
#)


db.define_table('pendedform',
    Field('table_name', 'string'),
    Field('hash', 'string', length=64, required=True, readable=False,
          writable=False, default=lambda: str(uuid.uuid4())),
    Field('instance_id', 'integer'),
)


db.define_table('pendedvalue',
    Field('form_id', 'reference pendedform'),
    Field('field_name', 'string'),
    Field('field_value', 'text'),
)


#db.define_table('balanco',
#)


#db.define_table('balanco_despesas',
#    Field('balanco_id', 'integer'),
#    Field('despesa_id', 'integer'),
#)


#db.define_table('balanco_receitas',
#    Field('balanco_id', 'integer'),
#    Field('receita_id', 'integer'),
#)


db.define_table('despesa',
    Field('descricao', 'string'),
    Field('natureza', 'string'),
    Field('valor', 'double'),
    Field('data', 'date'),
)


db.define_table('convenio',
    Field('table_name', 'string', required=True, requires=IS_IN_SET(('grupo',))),
    Field('object_id', 'integer', required=True),
    Field('agencia', 'string', length=15, required=True),
    Field('conta', 'string', length=20, required=True),
    Field('banco', 'string', length="2", default="bb",
          requires=IS_IN_SET([('bb', 'Banco do Brasil')],)),
    Field('cedente', 'string', comment=u"Razão social ou nome fantasia da empresa. Nome do titular da conta"),
    Field('convenio', 'string', comment=u"Muito cuidado com este número pois um digito errado irá implicar no não recebimento do valor pago!!"),
    Field('carteira', 'string', requires=IS_IN_SET(('18',)), comment=u"Número que deve ser obtido no banco. Este número varia de acordo com a modalidade de cobrança escolhida" ),
)


db.define_table('boleto',
    Field('convenio_id', 'reference convenio', required=True),
    Field('nosso_numero', 'integer', required=True),
    Field('numero_documento', 'string', required=True),
    Field('pessoa_id', 'reference pessoa'),
    Field('valor', 'double', required=True),
    Field('valor_pago', 'double'),
    Field('vencimento', 'date'),
    Field('sinalizar_pago', 'boolean'),
    Field('trash', 'boolean'),

    common_filter = lambda query: db.boleto.trash==False,
)


# Relaciona quais objetos compoe o boleto
db.define_table('boleto_objeto',
    Field('boleto_id', 'reference boleto'),
    Field('table_name', 'string', required=True),
    Field('object_id', 'integer', required=True),
)


db.define_table('receita',
    Field('descricao', 'string'),
    Field('patrocinador_id', 'integer'),
    Field('natureza', 'string'),
    Field('valor', 'double'),
    Field('data', 'date'),
    Field('vinculo', 'string'),
)


db.define_table('grupo',
    Field('nome', 'string', comment="Insira o nome do Grupo",
          represent=lambda nome, row: db_utils.grupo_nome_represent(db, nome, row)),
    Field('data_fundacao', 'date', comment="Data em que seu grupo foi criado"),
    Field('historico', 'text', widget=bootstrap_editor,
          comment="Insira informações a respeito do seu grupo"),
    Field('cidade_id', 'reference cidade', label="Cidade",
          widget=Autocomplete(URL('default', 'get_cidade', extension='json'),
                              format=db.cidade._format).widget,
          requires=IS_EMPTY_OR(IS_IN_DB(db, 'cidade.id')),
          comment="A cidade onde seu grupo está instalado" ),
    Field('curso', 'string'),
    Field('instituicao_id', 'reference pessoa_juridica', label="Instituição",
            requires=IS_EMPTY_OR(IS_IN_DB(db, 'pessoa_juridica.id'))),
#    Field('tutor_id', 'integer', label="Tutor"),
    Field('slug', 'string', readable=False,
          compute=lambda row: db_utils.grupo_slug_compute(db, row)),
    Field('foto', 'upload',
            uploadfolder=os.path.join(request.folder, 'uploads', 'grupos', 'photos') ),
    Field('miniatura', 'upload',uploadfolder=os.path.join(request.folder, 'uploads', 'grupos', 'photos'),
          compute=lambda row: THUMB(row.foto,folder=['uploads', 'grupos', 'photos']) ),
    Field('ativo', 'integer', **RWF),
    Field('configuracao_id', 'integer', **RWF),
    Field('email', 'string'),
    Field('pessoa_id', 'reference pessoa',
          requires=IS_EMPTY_OR(IS_IN_DB(db, 'pessoa.id')),unique=True, **RWF),
    Field('twitter', 'string'),
    Field.Method('get_related', lambda row, table:\
            db(db[table]['grupo_id']==row.grupo.id) ),

    format = lambda row: db_utils.grupo_format(db, row),
)


db.define_table('integrante',
    Field('pessoa_id', 'reference pessoa', required=True, **RWF),
    Field('grupo_id', 'reference grupo', required=True, **RWF),
    Field('tipo', 'string', required=True,
            requires=IS_IN_SET(db_utils.INTEGRANTE_TIPO)),
    Field('nasc', 'date'),
    Field('endereco', 'string'),
    Field('orkut', 'string'),
    Field('lattes', 'string'),
    Field('ing_Facu', 'date'),
    Field('ing_Pet', 'date'),
    Field('ing_Bolsa', 'date'),
    Field('saida_Bolsa', 'date'),
    Field('saida_Pet', 'date'),
    format=lambda r: r.pessoa_id,
)


db.define_table('atividade',
    Field('grupo_id', 'reference grupo', required=True, **RWF),
    Field('nome', 'string', required=True),
    Field('tipo', 'string', required=True,
          represent=lambda v, row: db_utils.ATIVIDADE_TIPOS[v],
          requires=IS_IN_SET(db_utils.ATIVIDADE_TIPOS)),
    Field('classificacao', 'string', label=u'Classificação',
          represent=lambda v, row: db_utils.ATIVIDADE_CLASSIFICACAO[v],
          requires=IS_IN_SET(db_utils.ATIVIDADE_CLASSIFICACAO)),
    Field('obs', 'string'),
    Field('descricao', 'text', label="Descrição",
          comment=db_utils.ATIVIDADE_DESCRICAO_COMMENT,
          widget=bootstrap_editor),
    Field('foto', 'upload',uploadfolder=os.path.join(request.folder, 'uploads', 'atividades', 'photos') ),
    Field('miniatura', 'upload',uploadfolder=os.path.join(request.folder, 'uploads', 'atividades', 'photos'),
          compute=lambda row: THUMB(row.foto, nx=200, ny=200,folder=['uploads', 'atividades', 'photos']) ),
    Field('certifica', 'boolean', label=u'Libera Certificado', comment=u"Marque este campo para indicar que esta atividade fornecerá certificados para os participantes que obtiverem a frequencia mínima"),
    Field('frequencia_minima', 'double', label='Frequência minima (%)', comment=u'Valor que representa a menor porcentagem de presença que o participante deve ter para receber o certificado. Caso não seja exigida uma frequência mínima deixe este campo em branco.'),
    Field('certificados_impressos', 'boolean', label='Certificado Liberado', comment=u"Marque este campo para informar que os certificados estão prontos. Além de aparecer uma mensagem na página inicial do evento informando que os certificados estão prontos os certificados só ficarão disponíveis na página do usuário se este campo estiver marcado."),
    Field('mini_relatorio', 'boolean', label="Mini relatório", comment=u"Marque este campo para informar que esta atividade requer mini-relatório"),
    Field('requer_inscricao', 'boolean', label="Requer Inscricao", comment=u"Marque este campo para indicar que os participantes devem se inscrever nesta atividade."),
    Field('instrucoes', 'text', label=u'Instruções', comment="Utilize este campo para passar as instruções relativas as inscrições aos usuários do portal", widget=bootstrap_editor),
    Field('msgonerror', 'text', comment=u"Utilize este campo para passar informações para que os usuários que estão encontrando dificuldade em se inscrever consigam resolver.", widget=bootstrap_editor),
    Field('tutorial', 'text', comment=u"Faça um breve tutorial de inscrição.", widget=bootstrap_editor),
    Field('tutorial_url', 'string', comment="Informe a url do tutorial. Note que se o campo anterior for preenxido apenas seu conteudo será apresentado", length=400),
    Field('insc_mestra', 'boolean', label='Requer a inscrição na Mestra', comment="Marque este campo para informar que para o participante se inscrever nesta atividade ele deve antes de se inscrito no evento correspondente."),
    Field('insc_online', 'boolean', label='Libera inscricao on-line', comment="Marque este campo para que os participantes possam se inscrever on-line."),
    Field('espera', 'boolean', label='Libera lista de espera', comment="Marque este campo para que as pessoas continuem se inscrevendo mesmo que o número máximo de inscritos seja alcançado. Observe que seus nomes ficam em uma lista de espera aguardando possíveis vagas."),
    Field('permuta', 'boolean', comment="Quando marcado permite que haja troca de inscrições até a data limite de inscrição"),
    Field('inicio_inscricao', 'date', label='Início Inscrição', comment="Data a partir da qual as inscrições serão liberadas. Note que se deixado em branco a inscrição estará disponível de imediato."),
    Field('termino_inscricao', 'date', label='Término Inscrição', comment="Data a partir da qual as inscrições serão encerradas. Note que, se deixado em branco as inscrições se encerrarão quando a atividade se iniciar."),
    Field('num_max', 'integer', label='Número máximo de Inscritos', comment="Número máximo de pessoas que podem participar desta atividade. Note que para o caso de eventos este número avaliará apenas as pessoas inscritas no evento, não levando em consideração as inscritas nas sub-atividades. Se deixado em branco 'infinitas' pessoas poderão se inscrever."),
    Field('valor', 'double', label='Valor da Inscricao'),
    Field('confirmacao', 'boolean', label='Requer Confirmação', comment='Quando marcado indica que o inscrito deverá confirmar que irá participar desta atividade até a data que você especificar. A confirmação é uma medida que visa evitar que as pessoas se inscrevam e se esqueçam de participar da atividade.'),
    Field('inicio_confirmacao', 'date', label='Início Confirmação', comment="Data a partir da qual se iniciará o período de confirmação. Uma boa prática é que esta data se inicie logo após o encerramento das inscrições para que os inscritos possam confirmar a presença na atividade. Note que se deixado em branco a confirmação estará disponível ao término das inscrições. "),
    Field('termino_confirmacao', 'date', label='Término Confirmação', comment="Data a partir da qual o período de confirmação se encerra. Quando utilizado em paralelo a lista de espera, é uma boa prática que esta data seja um ou dois dias antes do início da atividade, este tempo serve para as pessoas se informaram a respeito de sua vaga. Note que se deixado em branco a confirmação vai até o inicio da atividade."),
    Field('limitantes', 'list:string', label='Combinações possíveis', comment='Este campo serve para limitar o número de atividades que uma pessoa pode se inscrever em um evento. Informe em cada linha da tabela uma combinação possível. Por exemplo, para limitar a uma palestra e 1 curso digite "um" em palestra e em curso na primeira linha, e caso existam outras opções, insira novas linhas com suas respectivas combinações.'),
    Field('num_chamadas', 'integer', label='Número de listas de presença', comment='Estimativa do número de vezes que se passará a lista de presença durante a atividades.'),
#    Field('balanco_id', 'integer'),
#    Field('configuracao_id', 'integer'),
    Field('divulgar', 'boolean', comment="Quando marcado, todos poderão ver esta atividade."),
    Field('slug', 'string', compute=lambda r: IS_SLUG()(r.nome)[0] ),
    format = lambda row: db_utils.atividade_format(db, row),
)


db.define_table('atividade_periodo',
    Field('atividade_id', 'reference atividade', required=True),
    Field('inicio', 'datetime', required=True),
    Field('termino', 'datetime', required=True),
    format=lambda r: "%s %s" %(date2str(r.inicio), date2str(r.termino) ) ,
)


db.define_table('divisao',
    Field('grupo_id', 'integer'),
    Field('nome', 'string'),
)


db.define_table('lotacao',
    Field('divisao_id', 'integer'),
    Field('organizacao_id', 'integer'),
    Field('pessoa_id', 'reference pessoa'),
)


db.define_table('organizacao',
    Field('content_type_id', 'integer'),
    Field('object_id', 'integer'),
    Field('descricao', 'text'),
    Field('data_ini', 'date'),
    Field('data_ter', 'date'),
)


db.define_table('acao',
    Field('table_name', 'string'),
    Field('object_id', 'integer'),
    Field('estado', 'string', requires=IS_IN_SET({'p':'Ação Pendente', 'r':'Processando', 'c':'Ação Concluido'}), default="p"),
    Field('error', 'boolean'),
    Field('errorinfo', 'text'),
)


db.define_table('acao_grupo',
    Field('titulo', 'string'),
    Field('data_solicitacao', 'datetime'),
    Field('data_processamento', 'datetime'),
    Field('showed', 'datetime'),
    Field('estado', 'string', requires=IS_IN_SET([('p', 'Ação Pendente'),('r', 'Processando'),('c', 'Ação Concluido')]), default="p"),
    Field('comentario', 'text'),
    Field('user_id', 'reference auth_user'),
)


db.define_table('acao_grupo_acoes',
    Field('acao_grupo_id', 'integer'),
    Field('acao_id', 'integer'),
)


db.define_table('arquivo',
    Field('nome', 'string', required=True),
    Field('keyword', 'list:string'),
    Field('tipo', 'string', requires=IS_IN_SET(
        {'1':'Arquivo', '2':'Apostila', '3':'Documento', '4':'Foto', '5':'Memorando',
         '6':'Mini-Relatório', '7':'Relatório', '8':'Requerimento', '9':'Ata eletrônica'}) ),
    Field('data', 'date', default=request.now),
    Field('arquivo', 'upload',),
    Field('comentario', 'text'),
    format="%(nome)s",
)


db.define_table('arquivotemporario',
    Field('arquivo', 'string'),
)


db.define_table('desenvolvedor',
    Field('pessoa_id', 'reference pessoa'),
    Field('func', 'string'),
    Field('inicio', 'date'),
    Field('ativo', 'integer'),
)


db.define_table('mailmessage',
    Field('subject'),
    Field('message', 'text', required=True),
    Field('mail_to', required=True, requires=IS_EMAIL()),
    Field('reply_to', requires=IS_EMPTY_OR(IS_EMAIL()), default=mail.settings.sender),
    Field('attachments', 'list:reference arquivo'),
    Field('sended', 'boolean'),
    Field('data_pedido', 'date', default=request.now),
    Field('data_envio', 'date'),
)


db.define_table('portal',
    Field('tema_id', 'integer'),
)


db.define_table('portal_desenvolvedores',
    Field('portal_id', 'integer'),
    Field('desenvolvedor_id', 'integer'),
)


db.define_table('sugestao',
    Field('pessoa_id', 'reference pessoa'),
    Field('pagina', 'string'),
    Field('descricao', 'text'),
    Field('prioridade', 'integer'),
    Field('status', 'integer'),
    Field('resumo', 'string'),
)


db.define_table('sugestao_desenvolvedores',
    Field('sugestao_id', 'integer'),
    Field('desenvolvedor_id', 'integer'),
)


db.define_table('admin_tools_dashboard_preferences',
    Field('user_id', 'integer'),
    Field('data', 'text'),
    Field('dashboard_id', 'string'),
)


db.define_table('django_flatpage',
    Field('url', 'string'),
    Field('title', 'string'),
    Field('content', 'text'),
    Field('enable_comments', 'integer'),
    Field('template_name', 'string'),
    Field('registration_required', 'integer'),
)


db.define_table('facebookprofile',
    Field('user_id', 'integer'),
    Field('facebook_id', 'integer'),
    Field('access_token', 'string'),
)


db.pessoa.cidade_id.requires = db.pessoa_fisica.cidade_estudo_id.requires = \
            IS_EMPTY_OR(IS_IN_DB(db, 'cidade.id', '%(nome)s'))

#db.pessoa.cidade_id.represent = db.pessoa_fisica.cidade_estudo_id.represent = db.cidade._format


#for r in db((db.mensagem.hash==None) | (db.mensagem.hash=='')).select():
#    create_hash(db, 'mensagem', r.id)

#  after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

from pessoa_utils import get_pessoa
global unreaded



db.pessoa._after_update.append(
    lambda s,f: s.update_naive(
        miniatura=db.pessoa.miniatura.compute(s.select().first())
    )
)



SQLFORM.formstyles.table3cols = bootstrap3
pessoa = get_pessoa(request, db,auth,force_auth=True)

unreaded = None
if pessoa:
    total_messages = db(
        (db.mensagem_destinatarios.pessoa_id==pessoa.pessoa.id) &
        (db.mensagem.id==db.mensagem_destinatarios.mensagem_id)
    ).count(distinct=True)
    
    readed_message = db(
        (db.mensagem_readers.mensagem_id==db.mensagem.id) &
        (db.mensagem_readers.pessoa_id==pessoa.pessoa.id) &
        ~(db.mensagem.de==pessoa.pessoa.id)
    ).count(distinct=True, cache=(cache.ram, 60))
    unreaded = total_messages - readed_message
                   


#if db._dbname=='sqlite' and 0:
#    index = [
##         ('artigo',['id', '']),
#         ('atividade',['id', 'nome']),
##         ('Atividade_atividade_autores', ''),
##         ('Atividade_atividade_avaliadores', ''),
##         ('Atividade_atividade_groups', 'atividade_groups'),
#         ('atividade_periodo',['id', 'atividade_id']),
##         ('atividade_responsaveis',['id', 'atividade_id']),
##         ('Atividade_atividade_sub_atividades', 'atividade_subatividades'),
##         ('Atividade_autor', 'autor'),
##          ('Atividade_avaliacao', 'avaliacao'),
##         ('Atividade_avaliador', 'avaliador'),
##         ('Atividade_certificado', 'certificado'),
##         ('Atividade_certificado_problema', 'certificado_problema'),
##         ('Atividade_certificados_modelo', 'certificados_modelo'),
##         ('Atividade_certificados_modelo_certificados', 'certificados_modelo_certificados'),
##         ('Atividade_detalhe_pagamento', 'atividade_pagamento'),
##         ('Atividade_detalhe_pagamento_nossos_numeros', 'atividade_boletos'),
##         ('Atividade_etiqueta', 'etiqueta'),
##         ('Atividade_grupo_inscricao', 'grupo_inscricao'),
##         ('Atividade_grupo_inscricao_inscritos', 'grupo_inscricao_inscritos'),
##         ('Atividade_inscrito', 'inscrito'),
##         ('Atividade_lista_presenca', 'lista_presenca'),
##         ('Atividade_lista_presenca_pessoas', 'lista_presenca_pessoas'),
##         ('Atividade_modelo_certificado', 'modelo_certificado'),
##         ('Atividade_modelo_certificado_emails', ''),
##         ('Atividade_modelo_certificado_include_inscritos', 'modelo_certificado_include_inscritos'),
##         ('Atividade_pagina', 'pagina'),
##         ('Atividade_periodo', 'atividade_periodo'),
##         ('Atividade_tipo_etiqueta', 'tipo_etiqueta'),
##         ('Atividade_versao', 'versao'),
#         ('cidade',['id', 'nome', 'estado_id']),
#         ('estado',['id', 'nome']),
##         ('CustomForms_pendedform', 'pendedform'),
##         ('CustomForms_pendedvalue', 'pendedvalue'),
##         ('Financeiro_balanco', ''),
##         ('Financeiro_balanco_despesas', ''),
##         ('Financeiro_balanco_receitas', ''),
##         ('Financeiro_convenio', 'convenio'),
##         ('Financeiro_despesa', ''),
##         ('Financeiro_numero_sequencial', 'boleto'),
##         ('Financeiro_receita', ''),
##         ('Grupo_arquivogrupo', ''),
##         ('Grupo_assunto', 'assunto'),
##         ('Grupo_automatizedpeoplegroup', 'automatizedpeoplegroup'),
##         ('Grupo_automatizedpeoplegroup_filtros', 'automatizedpeoplegroup_filtros'),
##         ('Grupo_egresso', ''),
##         ('Grupo_entidade', 'pessoa_juridica'),
##         ('Grupo_funcao', 'funcao'),
#         ('grupo',['id', 'nome']),
##         ('Grupo_grupo_peoplegroups', 'grupo_peoplegroups'),
#         ('integrante',['id', 'grupo_id', 'pessoa_id']),
##         ('Grupo_juntarse_grupo', 'juntarse_grupo'),
##         ('Grupo_organizacao', 'organizacao'),
##         ('Grupo_organizacao_funcoes', ''),
##         ('Grupo_pauta', 'pauta'),
##         ('Grupo_post', 'post'),
##         ('Grupo_queryfiltro', 'queryfiltro'),
##         ('Grupo_responsavel', 'responsavel'),
##         ('Grupo_responsavel_responsaveis', 'responsavel_responsaveis'),
##         ('Grupo_reuniao', 'reuniao'),
##         ('Grupo_reuniao_ausentes', 'reuniao_ausentes'),
##         ('Grupo_reuniao_topicos', 'reuniao_topicos'),
##         ('Grupo_topico', 'topico'),
##         ('Grupo_topico_pautas', 'topico_pautas'),
##         ('Grupo_topico_responsaveis', 'topico_responsaveis'),
##         ('Grupo_tutor', ''),
##         ('Grupo_tutor_egresso', ''),
##         ('Organizacao_divisao', 'divisao'),
##         ('Organizacao_lotacao', 'lotacao'),
##         ('Organizacao_organizacao', 'atividade_organizador'),
##         ('Pessoa_contato_pessoa', 'pessoa_contato'),
##         ('Pessoa_mensagem', 'mensagem'),
##         ('Pessoa_mensagem_destinatarios', 'mensagem_destinatarios'),
##         ('Pessoa_mensagem_readers', 'mensagem_readers'),
##         ('Pessoa_mensagem_respostas', ''),
##         ('Pessoa_peoplegroup', 'peoplegroup'),
##         ('Pessoa_peoplegroup_pessoas', 'peoplegroup_pessoas'),
#         ('pessoa',['id', 'nome']),
#         ('pessoa_fisica',['id', 'pessoa_id']),
##         ('Portal_acao', 'acao'),
##         ('Portal_acao_grupo', 'acao_grupo'),
##         ('Portal_acao_grupo_acoes', 'acao_grupo_acoes'),
##         ('Portal_arquivo', 'arquivo'),
##         ('Portal_arquivotemporario', ''),
##         ('Portal_desenvolvedor', 'desenvolvedor'),
##         ('Portal_mailmessage', 'mailmessage'),
##         ('Portal_portal', 'portal'),
##         ('Portal_portal_desenvolvedores', 'portal_desenvolvedores'),
##         ('Portal_sugestao', 'sugestao'),
##         ('Portal_sugestao_desenvolvedores', 'sugestao_desenvolvedores'),
##         ('Portal_upload', ''),
##         ('admin_tools_dashboard_preferences', ''),
##         ('auth_group', 'auth_group'),
##         ('auth_group_permissions', ''),
##         ('auth_message', ''),
##         ('auth_permission', ''),
##         ('auth_user', 'auth_user'),
##         ('auth_user_groups', ''),
##         ('auth_user_user_permissions', ''),
##         ('authority_permission', ''),
##         ('django_admin_log', ''),
##         ('django_content_type', ''),
##         ('django_evolution', ''),
##         ('django_flatpage', ''),
##         ('django_flatpage_sites', ''),
##         ('django_project_version', ''),
##         ('django_session', ''),
##         ('django_site', ''),
##         ('facebook_facebookprofile', ''),
##         ('registration_registrationprofile', '')
#    ]

#    for table,indexes in index:
#        for i, col in enumerate(indexes):
#            name = 'idindex' if i==0 else "%s_%s" %(table, col)
#            c = 'CREATE INDEX IF NOT EXISTS %s ON %s (%s);' %(name,table, col)
#            print c
#            db.executesql(c)



#for t in db._tables:
#    print t
#    a=db(db[t].id>0).select(limitby=(0,1))

