# -*- coding: utf-8 -*-

from gluon import DIV,A,INPUT,BUTTON,SPAN,SCRIPT,FIELDSET,CAT,URL
from gluon import LABEL,SELECT,TEXTAREA,XML,current,I,BR,IMG
from gluon.sqlhtml import UploadWidget

response = current.response
T = current.T

def bootstrap3(form, fields):
    ''' bootstrap 3 format form layout '''
    form.add_class('form-horizontal')
    parent = FIELDSET()
    for id, label, controls, help in fields:
        # wrappers
        _help = SPAN(help, _class='help-block')
        # embed _help into _controls
        _controls = DIV(controls, _help, _class='col-lg-6')
        # submit unflag by default
        _submit = False
        if isinstance(controls, INPUT):
            controls.add_class('col-lg-6')

            if controls['_type'] == 'submit':
                # flag submit button
                _submit = True
                controls['_class'] = 'btn btn-primary pull-right'
            if controls['_type'] == 'button':
                controls['_class'] = 'btn btn-default'
            elif controls['_type'] == 'file':
                controls['_class'] = ' '.join([controls['_class']] + ['input-file'])
            elif controls['_type'] == 'text':
                controls['_class'] = 'form-control'
            elif controls['_type'] == 'password':
                controls['_class'] = 'form-control'
            elif controls['_type'] == 'checkbox':
                controls['_class'] = 'checkbox'



        # For password fields, which are wrapped in a CAT object.
        if isinstance(controls, CAT) and isinstance(controls[0], INPUT):
            controls[0].add_class('col-lg-2')

        if isinstance(controls, SELECT):
            controls.add_class('form-control')

        if isinstance(controls, TEXTAREA):
            controls.add_class('form-control')

        if isinstance(label, LABEL):
            label['_class'] = 'col-lg-3 control-label'


        if _submit:
            # submit button has unwrapped label and controls, different class
            parent.append(DIV(label, DIV(controls,_class="col-lg-6 col-lg-offset-2"), _class='form-group', _id=id))
            # unflag submit (possible side effect)
            _submit = False
        else:
            # unwrapped label
            parent.append(DIV(label, _controls, _class='form-group', _id=id))
    return parent


class Autocomplete(object):
    def __init__(self,url,show_result=True,add_link=False,tablename=None,format=lambda v: v,**kwargs):
        self.url = url
        self.show_result = show_result
        self.add_link = add_link
        self.format=format
        self.tablename = tablename
        self.kwargs=kwargs
        
    def widget(self,field, value):
        self.tablename = self.tablename or field._tablename
        _name=field.name,
        _id="%s_%s" % (self.tablename, field.name)
        
        self.kwargs.update({
                             '_type': "text",
                             '_name': "%s_text" %field.name,
                             '_id': "%s_%s_text" % (self.tablename, field.name),
                             '_value': '' if self.show_result else self.format(value),
                             '_class': "bt_autocomplete form-control",
                             '_data-url': self.url,
                             '_data-resume': 'true' if self.show_result else 'false'})
        
        kwargs = self.kwargs
        
        element = DIV(INPUT(_type="hidden",_name=field.name,_id="%s_%s" %(self.tablename, field.name),_value=value,_class="typeahead"),
                      INPUT(**kwargs),
                      _class="input-group" ) 
        if not self.show_result:
            element.append(
                        SPAN(BUTTON("Adicionar!",_class="btn btn-sm disabled",
                                    _type="button",_id="id_add_%s" %field.name,
                                    _title="Clique para adicionar",_disabled="disabled"),
                             _class="input-group-btn" )
                  )
    #    else:
    #        widget +=INPUT(_type="text",_name="%s_text" %field.name,
    #                       _id="%s_%s_text" % (self.tablename, field.name),
    #                       _value=value,
    #                       _class="bt_autocomplete") # {{ extra_attrs }} />
#        widget = element
        if self.add_link:
            element.append( 
                        SPAN( A(I(_class="icon-plus"),_href="",_class="btn btn-sm add-another addlink",
                                _id="add_%s_%s_text" % (self.tablename, field.name),
                                _onclick="return showAddAnotherPopup(this);"),
                             _class="input-group-btn" ) )
        if self.show_result:
            element+=DIV(
                        A(I(_class="icon-trash")," ",self.format(value) if callable(self.format) else self.format %value,
                              _id="%s_%s_trash" %(self.tablename, field.name),
                              _class="btn btn-sm",
                              _title="Clique para remover") if value else "",
                        _id="%s_%s_on_deck" %(self.tablename, field.name),
                        _class="resume",
                        _style="margin-top:5px;"
            )
#        element += 
        return element


def bootstrap_editor (field, value):
#    response.files.append(URL('static','assets/js/wysiwyg-conf.js'))
    return  (INPUT(_value=XML(value or '',sanitize=True),
                  _id="%s_%s" % (field._tablename, field.name),
                  requires=field.requires,
                  _name=field.name,
                  _type='hidden') +
            DIV(XML(value or ''),#_name=field.name,
             _for="%s_%s" % (field._tablename, field.name),
             _class='wysiwyg-editor',
             _type='text') )
             #_value=value)
#                 requires=field.requires),SCRIPT


def datepicker(field,value):
    from myutils import date2str
    return DIV(
		        INPUT(_class="form-control date-picker",_id="%s_%s" % (field._tablename, field.name),
		              _name=field.name,_type="text",requires=field.requires,_value=date2str(value),
		              _placeholder=T('Y-m-d'), **{'_data-date-format':T('Y-m-d')}),
		        SPAN(I(_class="icon-calendar bigger-110"),
		             _class="input-group-addon"),
	            _class="input-group"
        )


class Fileinput(UploadWidget):
    def __init__(cls,image=False):
        cls.image = True
        cls.DEFAULT_WIDTH = 80
        
    def widget(cls, field ,value, download_url=None, **attributes):
        attributes.update({'_class':"file-ace"})
        
#        if value:
#            attributes.update({'_data-file':field.retrieve(value)[0]})
        return super(Fileinput,cls).widget(field ,value, download_url=download_url, **attributes)
    
    
          
    
    
