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
