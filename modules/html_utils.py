#-*- coding: utf-8 -*-
from random import randint
from datetime import date
from gluon import (
    current,
    XML, 
    MENU, 
    UL,
    URL, 
    LI, 
    A, 
    SPAN,
    DIV,
    B,
    TAG,
)


T = current.T

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
                              B(_class="arrow fa fa-angle-down"),
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


class Paginate(object):
    def __init__(self, request, s, itens_page=10, show=True,
                 select_args=[], select_kwargs={}, search_url=None,
                 max_pages=5, info="%s"):
        self.s = s
        self.items_page = itens_page-1
        self.select_args = select_args
        self.select_kwargs = select_kwargs
        self.request = request
        self.search_url = search_url
        self.current_page = int(self.request.get_vars.get('page', '0'))
        self.max_pages = max_pages
        self.info = info
        self.show = show
#        self.page = int(self.request.get_vars.get('page', '0'))
#        self.render()

    @property
    def rows(self):
        limitby = (
            self.current_page * self.items_page,
            (self.current_page + 1) * self.items_page + 1)
        self.select_kwargs.update(dict(limitby=limitby))
        return self.s.select(*self.select_args, **self.select_kwargs)

    def render(self):
        vars = self.request.vars.copy()
        nav = TAG['nav']()
        nav.append(UL(_class="pagination"))

        num_items = self.s.count()
        num_pages = int(num_items / self.items_page) + 1

        if num_pages > 1:
            if num_pages < self.max_pages:
                range_ = (1, num_pages + 1)
            else:
                if self.current_page - 2 > 0:
                    range_ = (self.current_page - 2, self.current_page + 3)
                else:
                    range_ = (1, self.max_pages + 1)

            if self.current_page > 1:
                vars['page'] = self.current_page - 1
                url = URL(self.request.application, self.request.controller,
                          self.request.function,
                          args=self.request.args, vars=vars)
                prev = LI(A(SPAN(XML('&laquo;'), **{'_aria-hidden': 'true'}),
                            _href=url, **{'_aria-label': 'Anterior'}))
                nav.element('ul').insert(0, prev)

            info = LI(A(T(self.info, num_items)), _class="disabled")
            nav.element('ul').insert(0, info)

            for i in range(*range_):
                vars['page'] = i
                url = URL(self.request.application, self.request.controller,
                          self.request.function,
                          args=self.request.args, vars=vars)

                kwargs = {}
                if i == self.current_page:
                    kwargs = {'_class': "active"}
                nav.element('ul').append(LI(A(i, _href=url), **kwargs))

            if self.current_page < num_pages:
                vars['page'] = self.current_page + 1
                url = URL(self.request.application, self.request.controller,
                          self.request.function,
                          args=self.request.args, vars=vars)

                next_ = LI(A(SPAN(XML('&raquo;'), **{'_aria-hidden': 'true'}),
                             _href=url, **{'_aria-label': 'Próxima'}))
                nav.element('ul').append(next_)

        return nav
