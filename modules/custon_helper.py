from gluon import DIV,A,LI,UL,XML,SPAN,URL,INPUT,I

class BREADCRUMB_DIV(DIV):
    """
    Used to build breadcrumbs

    Example:
        breadcrumb = BREADCRUMB([(URL(...),title_page),(URL(...),title_page),...] )
        {{=breadcrumb}}
    """

    def __init__(self, data, **args):
        self.data = data
        self.attributes = args
        if not '_class' in self.attributes:
            self['_class'] = 'breacrumb'
        if not 'a_class' in self.attributes:
            self['a_class'] = 'a_breadcrumb'

    def serialize(self, data):
        div = DIV(**self.attributes)
        for item in data[:-1]:
            (link, name) = item
            a = A(name, _href=link,_class=self['a_class'])
            div.append(a)
        div.append(data[-1][1])
        return div

    def xml(self):
        return self.serialize(self.data).xml()

class BREADCRUMB(LI):
    """
    Used to build breadcrumbs

    Example:
        breadcrumb = BREADCRUMB([(URL(...),title_page),(URL(...),title_page),...] )
        {{=breadcrumb}}
    """

    def __init__(self, data, **args):
        self.data = data
        self.attributes = args

    def serialize(self, data):
        ul = UL(**self.attributes)
        for item in data[:-1]:
            (link, name) = item
            a = (A(name, _href=link),SPAN('/',_class="divider"))
            ul.append(a)
        ul.append(data[-1][1])
        return ul

    def xml(self):
        return self.serialize(self.data).xml()

class Paginate(object):
    def __init__(self,request,response,s,itens_page=10,select_args=[],select_kwargs={},search_url=None):
        self.s=s
        self.items_page=itens_page-1
        self.select_args=select_args
        self.select_kwargs=select_kwargs
        self.request=request
        self.response = response
        self.search_url = search_url
        self.render()

    @property
    def rows(self):
        page=int(self.request.get_vars.get('page','0')) - 1
        limitby=(page*self.items_page,(page+1)*self.items_page+1)
        self.select_kwargs.update(dict(limitby=limitby))
        return self.s.select(*self.select_args,**self.select_kwargs)

    def render(self):
        s = u'<a class="%(class)s" href="#" onclick="window.location.replace(setUrlVars({'+"'page'"+':%(page)s}));" title="%(page)s">%(page_text)s</a>'
        page=int(self.request.get_vars.get('page','1'))
        limitby=(page*self.items_page,(page+1)*self.items_page+1)
        def range_objects_page(num_items,num_pages,page):
            bottom = (page - 1) * self.items_page + 1 if num_items else 0
            top = bottom + self.items_page - 1
            if top >= num_items:
                top = num_items
            return bottom,top

        num_items = self.s.count()
        num_pages = int(num_items/self.items_page) + 1
        bottom,top =  range_objects_page(num_items,num_pages,page)
        page_nv=''
        if num_pages > 1:
            if page > 1:
                d={'page':page-1,'class':"btn",'page_text':u'<i class="icon-double-angle-left"></i>'}
                page_nv=s %d
                
            page_nv+=u'<button class="btn dropdown-toggle" data-toggle="dropdown"><b>%s - %s</b> de <b>%s</b></button>' %(bottom,top,num_items)
            page_nv+='<ul class="dropdown-menu">'
            for p in range(1,num_pages+1):
                bottom,top = range_objects_page(num_items,num_pages,p)
                d={'page':p,'class':"",'page_text':u'<b>%i - %i</b>' %(bottom,top)}
                aux = s %d
                page_nv+=u'<li>%s</li>' %aux
            page_nv+="</ul>"
        else:
            page_nv=u'<button class="btn" ><b>%s - %s</b> de <b>%s</b></button>' %(bottom,top,num_items)

        if page < num_pages:
            d={'page':page+1,'class':"btn",'page_text':u'<i class="icon-double-angle-right"></i>'}
            page_nv+=s %d

        page_nv = '<div class="btn-group pull_right">%s</div>' %(page_nv)
        
        
        if self.search_url:
            page_nv = DIV(
                DIV(
                    INPUT(_type="text",_placeholder="Pesquisar ...",_class="search_tool",_autocomplete="off",**{'_data-url':self.search_url} ),
                    _class="col-xs-9"
                ),
                DIV(XML(page_nv),_class="col-xs-3"),
                _class="row"
            )
        self.response.num_items = num_items
        self.response.paginate = XML(page_nv)


class AUTORIZED_MENU(object):
    def __init__(self,data):
        self.data = data

    def get_autorized(self, data):
        for i,item in enumerate(data):
            item_len = len(item)

            if item_len > 4 and not item[4]:
                data.pop(i)
                continue

            if item_len > 3: self.get_autorized(item[3])
        return data

    @property
    def autorized(self):
        return self.get_autorized(self.data)
