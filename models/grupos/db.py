# -*- coding: utf-8 -*-
from gluon.custom_import import track_changes; track_changes(True)

from reuniao_utils import (reuniao_topico_set,reuniao_ausentes_set,reuniao_participantes_set,
                           topico_responsaveis_set,topico_pautas_set,
                           topico_posts_set,reuniao_number,topico_close,topico_status_class,
                           topico_status)

db.define_table('arquivo_grupo',
    Field('grupo_id','reference grupo'),
    Field('arquivo_id','reference arquivo'),
#    common_filter = lambda query: db.arquivo_grupo.arquivo_id==db.arquivo.id,
    migrate=MIGRATE)


db.define_table('assunto',
    Field('table_name',requires=IS_EMPTY_OR(IS_IN_SET(db.tables)) ),
    Field('object_id','integer'),
    Field('assunto','string'),
    Field('grupo_id','reference grupo'),
    format="%(assunto)s",
    migrate=MIGRATE)


db.define_table('automatizedpeoplegroup',
    Field('grupo_id','integer'),
    Field('peoplegroup_id','integer'),
    migrate=MIGRATE)


db.define_table('automatizedpeoplegroup_filtros',
    Field('automatizedpeoplegroup_id','integer'),
    Field('queryfiltro_id','integer'),
    migrate=MIGRATE)


db.define_table('funcao',
    Field('grupo_id','integer'),
    Field('funcao','string'),
    migrate=MIGRATE)


db.define_table('grupo_peoplegroups',
    Field('grupo_id','integer'),
    Field('grupousergroup_id','integer'),
    migrate=MIGRATE)


db.define_table('juntarse_grupo',
    Field('grupo_id','reference grupo',required=True),
    Field('pessoa_id','reference pessoa',required=True),
    Field('form_id','reference pendedform',required=True),
    Field('rejeitada','boolean',default=False),
    migrate=MIGRATE)


db.define_table('queryfiltro',
    Field('nome','string'),
    Field('field','string'),
    Field('value','string'),
    migrate=MIGRATE)


db.define_table('responsavel',
    Field('funcao_id','integer'),
    Field('descricao','text'),
    migrate=MIGRATE)


db.define_table('responsavel_responsaveis',
    Field('responsavel_id','integer'),
    Field('pessoa_id','integer'),
    migrate=MIGRATE)


db.define_table('pauta',
    Field('nome','string',required=True),
    Field('grupo_id','reference grupo',required=True,writable=False,readable=False),
    format="%(nome)s",
    migrate=MIGRATE)


db.define_table('post',
    Field('topico_id','reference topico',required=True),
    Field('autor_id','reference pessoa',required=True),
    Field('data','date',required=True,writable=False,readable=False,default=request.now),
    Field('texto','text',required=True,widget=bootstrap_editor,requires=IS_NOT_EMPTY()),
    Field('closed','boolean',default=False),
#    format="%(topico_id)s",
    migrate=MIGRATE)


db.define_table('reuniao',
    Field('grupo_id','reference grupo',required=True,writable=False,readable=False),
    Field('inicio','datetime',default=request.now),
    Field('termino','datetime'),
    Field('pauta_id','reference pauta',required=True,label="Pauta"),
    Field('secretario_id','reference pessoa',required=True),
    Field('arquivo_id','reference arquivo'),
    Field('updated','datetime',compute=lambda r: request.now),
    Field('hash',length=64, default=lambda:str(uuid.uuid4())),
    Field.Method('topicos_set',lambda row,extra_query=None: reuniao_topico_set(db,row,extra_query) ),
    Field.Method('ausentes_set',lambda row,extra_query=None: reuniao_ausentes_set(db,row,extra_query) ),
    Field.Method('number',lambda row: reuniao_number(db,row.reuniao) ),
    Field.Method('participantes_set',lambda row,extra_query=None: reuniao_participantes_set(db,row,extra_query) ),

    format=lambda r: u"Reunião nº %s/%s" %(r.number(),r.inicio.year),
    migrate=MIGRATE)


db.define_table('reuniao_ausentes',
    Field('reuniao_id','reference reuniao',required=True),
    Field('pessoa_id','reference pessoa',required=True),
    migrate=MIGRATE)


db.define_table('reuniao_topicos',
    Field('reuniao_id','reference reuniao',required=True),
    Field('topico_id','reference topico',required=True),
    migrate=MIGRATE)


db.define_table('topico',
    Field('assunto_id','reference assunto',label="Assunto",
          widget=Autocomplete(URL('grupos','assunto',extension='json'),
                              show_result=False,
                              #add_link=URL('grupos','assunto',extension='json'),
                              format=db.cidade._format).widget),
    Field('texto','text',required=True,widget=bootstrap_editor,requires=IS_NOT_EMPTY()),
    Field('comentario','text',label="Comentário",widget=bootstrap_editor),
    Field('grupo_id','reference grupo',required=True,writable=False,readable=False),
    Field('data','date',default=request.now,required=True,writable=False,readable=False),
    Field('limite','date',widget=datepicker),
    Field('data_acao','date',widget=datepicker),
    Field('closed','boolean',writable=False,readable=False),
    Field('encerrado','boolean'),
    Field.Method('responsaveis_set',lambda row,extra_query=None: topico_responsaveis_set(db,row,extra_query) ),
    Field.Method('pautas_set',lambda row,extra_query=None: topico_pautas_set(db,row,extra_query) ),
    Field.Method('posts_set',lambda row,extra_query=None: topico_posts_set(db,row,extra_query) ),
    Field.Method('close',lambda row,topico: topico_close(db,row,topico) ),
    Field.Virtual('status_class',lambda row: topico_status_class(row.topico)),
    Field.Virtual('status',lambda row: topico_status(row.topico)),
    format=lambda r: "%s - %s" %(r.assunto_id.assunto, r.texto),
    migrate=MIGRATE)


db.define_table('topico_pautas',
    Field('topico_id','reference topico',required=True),
    Field('pauta_id','reference pauta',required=True),
    migrate=MIGRATE)


db.define_table('topico_responsaveis',
    Field('topico_id','reference topico',required=True),
    Field('pessoa_id','reference pessoa',required=True),
    migrate=MIGRATE)
