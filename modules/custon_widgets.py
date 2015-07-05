# -*- coding: utf-8 -*-
from gluon import SQLFORM,DIV,A,I,URL,current,SPAN

T = current.T
response = current.response
class SingleOptionsWidgetFK(SQLFORM.widgets.options):

    def __init__(self,response,url_args=None,url_kwargs={},*args,**kwargs):
        super(SingleOptionsWidgetFK,self).__init__(*args,**kwargs)
        self.url_args=url_args
        self.url_kwargs=url_kwargs
        self.response = response


    def widget(self,field,value):
        self.response.files.append(URL('static','css/colorbox.css'))
        self.response.files.append(URL('static','js/jquery.colorbox-min.js'))
        self.response.files.append(URL('static','js/RelatedObjectLookups.js'))
        if not vars in self.url_kwargs:
            self.url_kwargs['vars']={}

        self.url_kwargs['vars'].update(
                                  {'popup':"%s_%s" %(field.table,field.name),
                                   'desmiss':True})

        rel = URL(*self.url_args,**self.url_kwargs)
        return DIV(
                    SQLFORM.widgets.options.widget(field,value),
                    A(I(_class="icon-circle-plus",_alt="%s" %T('Add Another'),
                        _title="clique para adicionar"),
                      _href="%s" %rel,_class="foreignkey btn",_id="add_id_%s" %field.name,
                      _onclick="return showAddAnotherPopup(this);"
                    ),
                    _class="input-append"
               )

class MultipleOptionsWidgetFK(SQLFORM.widgets.multiple):

    def __init__(self,url_args=None,url_kwargs={},response=response,*args,**kwargs):
        super(MultipleOptionsWidgetFK,self).__init__(*args,**kwargs)

        self.url_args=url_args
        self.url_kwargs=url_kwargs

    def widget(self,field,value):
        if not vars in self.url_kwargs:
            self.url_kwargs['vars']={}

        self.url_kwargs['vars'].update(
                                  {'popup':"%s_%s" %(field.table,field.name),
                                   'desmiss':True})

        rel = URL(*self.url_args,**self.url_kwargs)
        return DIV(
                    SQLFORM.widgets.multiple.widget(field,value,_class="form-control"),
                    SPAN(A(I(_class="icon-plus",_alt="%s" %T('Add Another'),
                            _title="clique para adicionar"),
                          _href="%s" %rel,_class="foreignkey",_id="add_id_%s" %field.name,
                          _onclick="return showAddAnotherPopup(this);"
                         ),
                         _class="input-group-addon"),
                    _class="input-group"
               )
