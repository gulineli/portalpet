# -*- coding: utf-8 -*-

from gluon import (
    A,
    DIV,
    LI,
    UL,
    XML,
    SPAN,
    TAG,
    URL,
    current
)

T = current.T


class BREADCRUMB_DIV(DIV):
    """
    Used to build breadcrumbs

    Example:
        breadcrumb = BREADCRUMB([(URL(...),title_page),(URL(...),title_page),])
        {{=breadcrumb}}
    """

    def __init__(self, data, **args):
        self.data = data
        self.attributes = args
        if '_class' not in self.attributes:
            self['_class'] = 'breacrumb'
        if 'a_class' not in self.attributes:
            self['a_class'] = 'a_breadcrumb'

    def serialize(self, data):
        div = DIV(**self.attributes)
        for item in data[:-1]:
            (link, name) = item
            a = A(name, _href=link, _class=self['a_class'])
            div.append(a)
        div.append(data[-1][1])
        return div

    def xml(self):
        return self.serialize(self.data).xml()


class BREADCRUMB(LI):
    """
    Used to build breadcrumbs

    Example:
        breadcrumb = BREADCRUMB([(URL(...),title_page),(URL(...),title_page),])
        {{=breadcrumb}}
    """

    def __init__(self, data, **args):
        self.data = data
        self.attributes = args

    def serialize(self, data):
        ul = UL(**self.attributes)
        for item in data[:-1]:
            (link, name) = item
            a = (A(name, _href=link), SPAN('/', _class="divider"))
            ul.append(a)
        ul.append(data[-1][1])
        return ul

    def xml(self):
        return self.serialize(self.data).xml()


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


class AUTORIZED_MENU(object):
    def __init__(self, data):
        self.data = data

    def get_autorized(self, data):
        for i, item in enumerate(data):
            item_len = len(item)

            if item_len > 4 and not item[4]:
                data.pop(i)
                continue

            if item_len > 3:
                self.get_autorized(item[3])
        return data

    @property
    def autorized(self):
        return self.get_autorized(self.data)
