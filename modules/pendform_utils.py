#-*- coding: utf-8 -*-
from gluon import SQLFORM,current
T = current.T
request = current.request

class PendForm(object):
    def __init__(self,db,pendedform=None,table_name=None,instance_id=None,fields=[]):

        self.pendedform = pendedform
        self.table_name = table_name
        self.instance_id = instance_id
        self.fields = fields
        self.db = db

    @property
    def hash(self):
        return self.pendedform.hash if self.pendedform else None

    @property
    def pendedform_id(self):
        return self.pendedform.id if self.pendedform else None

    def create_or_update(self,values={}):
        db = self.db
        if not self.pendedform:
            pendedform_id = db.pendedform.insert(table_name=self.table_name,instance_id=self.instance_id)
            self.pendedform = db.pendedform[pendedform_id]

        pendedform_id = self.pendedform.id
        for field,value in values.items():
            value = unicode(value) if value else ''##str(getattr(getattr(db,self.table_name),field).validate(value) )
            db.pendedvalue.update_or_insert(
                (db.pendedvalue.form_id == pendedform_id) & (db.pendedvalue.field_name == field),
                field_value = value,form_id = pendedform_id, field_name = field)

        return self.pendedform

    @property
    def form (self):
#        request.vars.lang = 'pt-br'
        db = self.db
        T.force(None)

        table = self.db[self.table_name]
        kwargs = dict(formstyle='bootstrap',showid=False)
        if self.instance_id:
            kwargs['record'] = table[self.instance_id]
        elif self.pendedform:
#            aux={}
            for f in table.fields:
                pendedvalue = db((db.pendedvalue.form_id==self.pendedform.id) &
                           (db.pendedvalue.field_name==f)).select().first()
                if pendedvalue:
                    field = table[f]

                    if not field.validate(pendedvalue.field_value)[1]:
#                        aux.update(**{f:field.validate(pendedvalue.field_value)[0]})
                        field.default=field.validate(pendedvalue.field_value)[0]
#                    else:
#                        field.default=pendedvalue.field_value
#            kwargs['record'] = table[table.insert(**aux)]
        T.force('pt-br')
        table = self.db[self.table_name]

        return SQLFORM(table,**kwargs)

#    def resume(self,pended_form):
#        form = pended_form
#        data=[]
#        for d in form.data.all():
#            if d.value and d.value[-1]==']' and d.value[0]=='[':
#                value = eval(d.value)
#            else: value= d.value
#            data.append((d.name,value))
#        return cls(dict(data))


#    resume = classmethod(resume)
