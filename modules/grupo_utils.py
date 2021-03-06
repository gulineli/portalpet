﻿#-*- coding: utf-8 -*-
from gluon import URL,XML,I,current,redirect,SPAN
from custon_helper import AUTORIZED_MENU

T = current.T
request = current.request

def grupo_menu(response,auth,grupo):
    response.menu = [
        # Junte-se a nos
        (
            (I(_class="menu-icon fa fa-sign-in"), SPAN(' ', T('Junte-se a nós'), _class="menu-text")),
             False, 
             URL('grupos', 'junte_se_a_nos',args=(grupo.slug,)), [],
             False
        ),
        # Solicitações de Inclusões
        (
            (I(_class="menu-icon fa fa-sign-in"), 
             SPAN(' ',
                  T('Sol. de Inclusão'),
                  ' (%s)' %grupo.get_related('juntarse_grupo').count(),
                  _class="menu-text")
            ),
            False, 
            URL('grupos', 'validar_inclusoes',args=(grupo.slug,)), [],
            True
        ),
        # Mensagens
#        ((I(_class="menu-icon fa fa-envelope"),SPAN(' ',T('Mensagens'),' (%s)' %grupo.get_related('juntarse_grupo').count(),_class="menu-text") ),
#         False, URL('grupos', 'grupo_message_box',args=(grupo.slug,)), [],True),
         # Nosso Grupo
        (
            (I(_class="menu-icon fa fa-group"), SPAN(' ', T('Nosso Grupo'), _class="menu-text")),
             False, 
             "",
             [
                 ((T('Dados do Grupo')),False, URL('grupos', 'grupo',args=(grupo.slug,)), []),
                 ((T('Integrantes')),False, URL('grupos', 'integrantes',args=(grupo.slug,)), []),
                 ((T('Egressos')),False, URL('grupos', 'integrantes',args=(grupo.slug,'e')), []),
             ]
        ),
        # Atividades
        (
            (I(_class="menu-icon fa fa-calendar"), SPAN(' ', T('Atividades'), _class="menu-text")),
            False, 
            URL('grupos', 'atividades',args=(grupo.slug,)), [],
            True
        ),
        # Arquivos
        (
            (I(_class="menu-icon fa fa-folder-open"), SPAN(' ', T('Arquivos'), _class="menu-text")),
            request.function=='arquivos', 
            URL('grupos', 'arquivos',args=(grupo.slug,)), [],
            True
        ),
        # Reuniões
        (
            (I(_class="menu-icon fa fa-book"), SPAN(' ', T('Reuniões'), _class="menu-text")),
             False,
             "",
             [
                 ((T('Nova')),False, URL('grupos', 'nova_reuniao',args=(grupo.slug,)), []),
                 ((T('Antigas')),False, URL('grupos', 'reunioes',args=(grupo.slug,)), []),
                 ((T('Tópicos')),False, URL('grupos', 'topicos',args=(grupo.slug,)), []),
                 ((T('Pautas')),False, URL('grupos', 'pautas',args=(grupo.slug,)), []),
             ]
        ),
        # Cadastrar
        (
            (I(_class="menu-icon fa fa-archive"), SPAN(' ', T('Cadastrar'), _class="menu-text")),
            False,
            URL('grupos', 'grupo_message_box',args=(grupo.slug,)),
             [
                 ((T('Arquivos')),False, URL('grupos', 'arquivos',args=(grupo.slug,)), []),
                 ((T('Atividades')),False, URL('grupos', 'atividades',args=(grupo.slug,)), []),
             ]
        ),
        # Gerenciar
        (
            (I(_class="menu-icon fa fa-compass"), SPAN(T('Gerenciar'), _class="menu-text")),
            False,
            URL('grupos', 'grupo_message_box',args=(grupo.slug,)),
             [
                 ((T('Integrantes')),False, URL('grupos', 'gerenciar_integrantes',args=(grupo.slug,)), []),
                 ((T('Egressos')),False, URL('grupos', 'gerenciar_egressos',args=(grupo.slug,)), []),
                 ((T('Contatos')),False, URL('grupos', 'gerenciar_contatos',args=(grupo.slug,)), []),
             ]
        ),
        # Configurações
        (
            (I(_class="menu-icon fa fa-cogs"), SPAN(' ', T('Configurações'), _class="menu-text")),
            False,
            URL('grupos', 'grupo_message_box',args=(grupo.slug,)),
            [
                ((T('Permissões de Acesso')),False, URL('grupos', 'configurar_permissoes',args=(grupo.slug,)), []),
                ((T('Temas')),False, URL('grupos', 'configurar_tema',args=(grupo.slug,)), []),
            ]
        ),

    ]
