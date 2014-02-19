#-*- coding: utf-8 -*-
from random import randint
from datetime import date
from gluon import XML,MENU,UL,LI,A,SPAN,DIV,B

class MENU_(MENU):
    def __init__(self, data, **args):
        super(MENU_,self).__init__(data, **args)
        if not 'a_submenu_class' in self.attributes:
            self['a_submenu_class'] = 'dropdown-toggle'

    def serialize(self, data, level=0):
        if level == 0:
            ul = UL(**self.attributes)
        else:
            ul = UL(_class=self['ul_class'])
        for item in data:
            if isinstance(item,LI):
                ul.append(item)
            else:
                (name, active, link) = item[:3]
                if isinstance(link, DIV):
                    li = LI(link)
                elif 'no_link_url' in self.attributes and self['no_link_url'] == link:
                    li = LI(DIV(name))
                elif isinstance(link,dict):
                    li = LI(A(name, **link))
                elif link:
                    li = LI(A(name, _href=link))
                elif not link and isinstance(name, A):
                    li = LI(name)
                else:
                    li = LI(A(XML(" ".join(map(lambda s: "%s" %s,name)) ),
                              B(_class="arrow icon-angle-down"),
                              _href='#',
                              _class=self['a_submenu_class'],))
                if level == 0 and item == data[0]:
                    li['_class'] = self['li_first']
                elif level == 0 and item == data[-1]:
                    li['_class'] = self['li_last']
                if len(item) > 3 and item[3]:
                    li['_class'] = self['li_class']
                    li.append(self.serialize(item[3], level + 1))
                if active or ('active_url' in self.attributes and self['active_url'] == link):
                    if li['_class']:
                        li['_class'] = li['_class'] + ' ' + self['li_active']
                    else:
                        li['_class'] = self['li_active']
                if len(item) <= 4 or item[4] == True:
                    ul.append(li)
        return ul
