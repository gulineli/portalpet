#-*- coding: utf-8 -*-
from random import randint
from itertools import groupby
import datetime

from gluon import URL,XML,I,current,redirect
T = current.T


def date2str(d,format=None):
    if not format:
        if isinstance(d, datetime.datetime):
            format = T('%Y-%m-%d %H:%M:%S')
        elif isinstance(d, datetime.date):
            format = T('%Y-%m-%d')
        elif isinstance(d, datetime.time):
            format = '%H:%M'
        else:
            return d
    return d.strftime(format=str(format) )


def datediff_T(diff,short=False):
    d = T("%s %%{dia}",diff.days) if diff.days else ""
    h = int(diff.seconds/3600)
    m = int((diff.seconds - h*3600)/60)
    s = diff.seconds -h*3600 - m*60
    m = T("%s %%{minuto}",m) if m else ""
    h = T("%s %%{hora}",h) if h else ""
#    s = T("%s %%{segundo}",s) if s else ""
    diffs = [unicode(u) for u in [d,h,m] if u]

    if len(diffs) > 1:
        if short:
            return XML('+ que %s' %diffs[0] )
        return XML(', '.join([unicode(u) for u in diffs[:-1] if u]) + ' e ' + unicode(diffs[-1]) )
    return XML(diffs[0] if len(diffs)>0 else unicode(T("%s %%{segundo}",s)) )


def cooldate(d, T=T,format=None):
    if isinstance(d, datetime.datetime):
        dt = datetime.datetime.now() - d
    elif isinstance(d, datetime.date):
        return date2str(d,format=format)
    elif not d:
        return ''
    else:
        return '[invalid date]'

    if dt.days < 0:
        suffix = ' from now'
        return date2str(d,format="%H:%M")
    else:
        return date2str(d,format=T('%Y-%m-%d'))


def render_fields(row,db,tables=[],exclude=[]):
    render=[]
    tables = [item  for item in row if isinstance(row[item],type(row))] if not tables else tables
    for table in tables:
        if row.get(table):
            render +=render_fields(row[table],db,tables=[table],exclude=exclude)
        else:
            for field in db.get(table).fields:
                if db[table][field].readable and not field=='id' and not field in exclude and row[field]:
                    if db[table][field].represent:
                        
                        render.append((db[table][field].label,
                                       db[table][field].represent(row[field],row) or '-'))
                    else:
                        render.append((db[table][field].label,XML(row[field] or '-' ) ))
    return render


def copydata(src, dest,db,tables=[]):
    ''' copy data for the listed from src to dest, only if they exist in the source
     it is chiefly used to populate fields in a created form
     Original from Jay Kelnar '''
    tables = [item  for item in src if isinstance(src[item],type(src))] if not tables else tables

    for table in tables:
        for k in db.get(table).fields:
            dest[k] = src[table][k]
    return dict()


def create_hash(db,table,id,field='hash'):
    hash = str(randint(100000000000,999999999999))
    while db(db[table][field]==hash).count():
        hash = str(randint(100000000000,999999999999))

    db[table][id].update_record(**{field:hash})


def regroup(obj_list,grouper):
    from gluon.storage import Storage
    if not obj_list:
        return []
    return [
        Storage(grouper=key, list=list(val) )
        for key, val in groupby(obj_list, lambda obj: obj[grouper])
    ]


def jeditable_func(f_globals,request):
    import re
    shout_id_re = re.compile('(?P<database>.*)-(?P<table>.*)-(?P<field>.*)-(?P<object_id>\d+)')
    m = shout_id_re.match(request.vars.get('id',''))
    database = f_globals.get(m.group('database'))
    table = m.group('table')
    field = m.group('field')
    object_id = m.group('object_id')
    value = request.vars.get('value')
    if all([database,table,field,object_id]):
        q = getattr(database,table).id == object_id
        record = getattr(database,table)[object_id]
        a=database(q).validate_and_update(**{field:value})
        represent = getattr(getattr(database,table),field).represent
        value = represent(value,record) if represent else value
    return XML(value)


def write_pdf(html,filename,stream=False,base_folder=''):
    import os
    import ho.pisa as pisa
    import cStringIO as StringIO
    pisa.showLogging()
    def fetch_resources(uri, rel):
        return os.path.join(base_folder,uri)

    path = os.path.join(base_folder,filename) + '.pdf'
    result = StringIO.StringIO() if stream else file(path, "wb")

    pdf = pisa.CreatePDF(
            html,
            result,
#            encoding='UTF-8',
            show_error_as_pdf=True,
#            link_callback=fetch_resources
            )

    if not stream:
        result.close()
        return  path #Retorna o caminho para o arquivo
    else:
        return result #Retorna o stream do arquivo
