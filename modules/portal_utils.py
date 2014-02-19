#-*- coding: utf-8 -*-
from random import randint

from gluon import URL,XML,I,current,redirect
T = current.T

def portal_menu(response,auth):
    response.submenu = [
        ((I(_class="icon-user"),' ',T('Perfil')), False, URL('default', 'pessoa'), []),
        ((I(_class="icon-list"),' ',T('Atividades')), False, URL('default','grupos'),[]),
        ((I(_class="icon-file"),' ',T('Artigos')), False, URL('default','atividades'),[]),
        ((I(_class="icon-blog"),' ',T('Arquivos/Apostilas')), False, URL('default','atividades'),[]),
        ((I(_class="icon-envelope"),' ',T('Mensagens')), False, URL('default','message_box'),[]),
        ((I(_class="icon-book-open"),' ',T('Albuns')), False, URL('default','sobre_o_pet'),[]),
    ]
