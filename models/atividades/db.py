
db.define_table('atividade_congresso',
    Field('atividade_id','reference atividade',required=True,unique=True),
    Field('data_limite_submissao','date'),
    Field('aceita_artigos','boolean',default=True),
    Field('num_artigos','integer',default=1),
    Field('num_autores','integer'),
    Field('dias_avaliacao','integer'),
    Field('prazo_correcao','integer'),
    Field('carta_aceite','text',comment=u"Insira o texto que deve ir para a carta de aceite. A carta de aceite será submetida quando o artigo for aprovado. Utilize 'artigo.autores' para inserir os autores do artigo, 'artigo.titulo' para inserir o titulo do artigo, 'atividade.nome' para inserir o nome da atividade e 'atividade.periodo' para inserir o periodo de realização da atividade"),
    Field('ficha_avaliacao','upload',uploadfolder=os.path.join(request.folder,'uploads','atividades','ficha_avaliacao') ),
    Field('num_artigos_grupo','integer'),
    Field('vincular_grupo','boolean'),
    migrate=MIGRATE
)


db.define_table('atividade_autores',
    Field('atividade_id','reference atividade'),
    Field('grupousergroup_id','integer'),
    migrate=MIGRATE)


##Atividade_avaliador - Substituida pela tabela avaiador apenas
db.define_table('avaliador',
    Field('atividade_id','reference atividade',required=True),
    Field('pessoa_id','reference pessoa',required=True),
    Field('areas_conhecimento','list:string'),
    migrate=MIGRATE)


db.define_table('atividade_groups',
    Field('atividade_id','reference atividade',required=True),
    Field('group_id','reference auth_group'),
    format="%(atividade_id)s",
    migrate=MIGRATE)


db.define_table('atividade_responsaveis',
    Field('atividade_id','integer'),
    Field('responsavel_id','integer'),
    migrate=MIGRATE)


db.define_table('atividade_subatividades',
    Field('mestra_id','reference atividade',required=True),
    Field('subatividade_id','reference atividade',required=True),
    migrate=MIGRATE)


##db.define_table('avaliador',
##    Field('pessoa_id','integer'),
##    Field('areas_conhecimento','string'),
##    migrate=MIGRATE)


db.define_table('certificado',
#    Field('content_type_id','integer'),
    Field('table_name','string',required=True),
    Field('object_id','integer',required=True),
    Field('modelo_id','reference modelo_certificado',required=True),
    Field('email_id','reference mailmessage'),
    Field('certificado','upload'),
    Field('num_pages','integer'),
    Field('liberado','boolean'),
    Field('processado_em','datetime'),
    Field('trash','boolean'),
    Field.Virtual('dono',
        lambda row: getattr(db,row.table)[row.object_id] ),
    migrate=MIGRATE)


db.define_table('certificado_problema',
    Field('certificado_id','integer'),
    Field('descricao','text'),
    Field('data','datetime'),
    Field('corrigido','integer'),
    Field('resolvido','integer'),
    migrate=MIGRATE)


db.define_table('certificados_modelo',
    Field('modelo_certificado_id','integer'),
    migrate=MIGRATE)


db.define_table('certificados_modelo_certificados',
    Field('certificados_modelo_id','integer'),
    Field('certificado_id','integer'),
    migrate=MIGRATE)


db.define_table('atividade_pagamento',
    Field('atividade_id','reference atividade',unique=True),
    Field('forma_pagamento','string',length=2,
            requires=IS_IN_SET([("av","Recebimento no ato da inscrição (presencial)"),
                                ("bo","Boleto Bancário"),
                                ('dp',"Depósito/Transferência bancária")]) ),
    Field('convenio_id','reference convenio'),
    Field('data_vencimento','date'),
    Field('instrucoes','text'),
    Field('gerar_boleto_por_grupo','boolean'),
    migrate=MIGRATE)


db.define_table('atividade_boletos',
    Field('atividade_id','reference atividade',required=True),
    Field('boleto_id','reference boleto',required=True),
    migrate=MIGRATE)


db.define_table('etiqueta',
    Field('nome','string'),
    Field('tipo_etiqueta_id','integer'),
    Field('atividade_id','integer'),
    Field('lista','string'),
    Field('texto','text'),
    migrate=MIGRATE)


db.define_table('grupo_inscricao',
    Field('grupo_id','integer'),
    Field('atividade_id','integer'),
    Field('finalizada','integer'),
    Field('valor_pago','double'),
    migrate=MIGRATE)


db.define_table('grupo_inscricao_inscritos',
    Field('grupo_inscricao_id','integer'),
    Field('inscrito_id','integer'),
    migrate=MIGRATE)


db.define_table('inscrito',
    Field('pessoa_id','reference pessoa',required=True),
    Field('atividade_id','reference atividade',required=True),
    Field('data_insc','datetime',default=request.now),
    Field('confirmado','boolean',default=False),
    Field('pago','boolean',default=False),
    Field('certificado2','string'),
    Field('valor_pago','double'),
    Field('barcode','string'),
    Field('code_verification','string'),
    Field('fake','boolean',default=False),
    Field('finalizada','boolean',default=False),
    Field('espera','boolean',default=False),
    migrate=MIGRATE)


db.define_table('delta_inscricao',
    Field('atividade_id','reference atividade',required=True),
    Field('data','date',default=request.now,required=True),
    Field('n_inscricao','integer',required=True),
    format="%(data)s - %(atividade_id)s - %(n_inscricao)s",
    migrate=MIGRATE
)


db.define_table('lista_presenca',
    Field('atividade_id','reference atividade',required=True),
    Field('n_lista','integer',required=True,default=1),
    Field('finalizada','boolean'),
    
    format = lambda r: "%s - %s" %(db.atividade._format %r.atividade_id,r.n_lista) ,
    migrate=MIGRATE)


db.define_table('lista_presenca_pessoas',
    Field('lista_presenca_id','reference lista_presenca',required=True),
    Field('pessoa_id','reference pessoa',required=True), ##antes inscrito_id
    migrate=MIGRATE)


db.define_table('modelo_certificado',
    Field('nome','string'),
    Field('atividade_id','integer'),
    Field('lista','string'),
    Field('certificados','string'),
    Field('processamento','datetime'),
    Field('last_update','datetime'),
    migrate=MIGRATE)


db.define_table('modelo_certificado_emails',
    Field('modelo_certificado_id','integer'),
    Field('mailmessage_id','integer'),
    migrate=MIGRATE)


db.define_table('modelo_certificado_include_inscritos',
    Field('inscrito_id','integer'),
    Field('modelo_certificado_id','integer'),
    migrate=MIGRATE)


db.define_table('pagina',
    Field('numero','integer'),
    Field('background','string'),
    Field('background_min','string'),
    Field('background_thumb','string'),
    Field('orientacao','string'),
    Field('texto','text'),
    Field('localdata','string'),
    Field('margens','string'),
    Field('modelo_certificado_id','integer'),
    Field('tx_reducao','double'),
    Field('tamanho','string'),
    migrate=MIGRATE)


db.define_table('tipo_etiqueta',
    Field('nome','string'),
    Field('largura','double'),
    Field('altura','double'),
    Field('pagina','string'),
    Field('orientacao','string'),
    Field('margem_superior','double'),
    Field('margem_direita','double'),
    Field('margem_inferior','double'),
    Field('margem_esquerda','double'),
    Field('h','double'),
    Field('d','double'),
    migrate=MIGRATE)


db.define_table('artigo',
    Field('dono_id','reference pessoa',required=True),
    Field('grupo_id','reference grupo',requires=IS_EMPTY_OR(IS_IN_DB(db,'grupo.id',db.grupo._format)) ),
    Field('avaliador_id','reference avaliador'),
    Field('atividade_id','reference atividade',required=True),
    Field('area_conhecimento','string'),
    migrate=MIGRATE)
    

av_parecer = {'ap':'Aprovado', 'am':'Aceito com Modificações', 're':'Rejeitado'}
db.define_table('avaliacao',
    Field('comentarios','text'),
    Field('parecer','string',requires=IS_IN_SET(av_parecer.items()),represent=lambda r,v:av_parecer[v] ),
    Field('data_avaliacao','date'),
    Field('liberar','boolean'),
    migrate=MIGRATE)
    
    
db.define_table('versao',
    Field('titulo','string',required=True),
    Field('arquivo','upload',uploadfolder=os.path.join(request.folder,'uploads','atividades','artigos')),
    Field('revisao','integer'), ##Antigo campo versao -> substituido para melhorar a leitura
    Field('avaliacao_id','reference avaliacao'),
    Field('data_envio','date',default=request.now),
    Field('artigo_id','reference artigo',required=True),
    Field('enviado','boolean'),
    migrate=MIGRATE)


db.define_table('autor',
    Field('versao_id','reference versao'), ##Adicionado
    Field('ordem','integer'),
    Field('pessoa_id','reference pessoa'),
    Field('nome','string'),
    Field('email','string',requires=IS_EMPTY_OR(IS_EMAIL()) ),
    migrate=MIGRATE)
    
    
#db.define_table('versao_autores',
#    Field('versao_id','integer'),
#    Field('autor_id','integer'),
#    migrate=MIGRATE)


def after_insert_inscrito(f,id):
    
    if not db((db.delta_inscricao.atividade_id==f.atividade_id) & \
              (db.delta_inscricao.data==f.data_insc) ).update(n_inscricao = db.delta_inscricao.n_inscricao + 1 ):
        
        db['delta_inscricao'].insert(atividade_id=f.atividade_id,
                                     n_inscricao=1,
                                     data=f.data_insc)


db.inscrito._after_insert.append(
    after_insert_inscrito 
)
    
