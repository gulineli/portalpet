# -*- coding: utf-8 -*-

###############################################################################
# Plugin - Admin Plus
# Copyright (C) 2014  Samuel Bonilla <pythonners@gmail.com>

# License: LGPLv3 (http://www.gnu.org/licenses/lgpl.html)
###############################################################################


#--------------- Menu opcional ------------------------
"""
 Example:

 settings.extra_sidebar_title = 'My new menu'

 settings.extra_sidebar = [ LI(A(I(_class="fa fa-angle-right"), ' google', _href="http://google.com")), \
                            LI(A(I(_class="fa fa-angle-right"), ' web2py', _href="http://web2py.com")), \
                        ]


"""

settings.extra_sidebar_title = ''

settings.extra_sidebar = [ #LI(A(I(_class="fa fa-angle-right"), ' google', _href="http://google.com")), \
                           #LI(A(I(_class="fa fa-angle-right"), ' web2py', _href="http://web2py.com")), \
                        ]

optimizar_paginacion = True
settings.items_per_page = 6 # if optimizar_paginacion else 0

#------------------ controladores ----------------------------

def install():
    """ Esta funcion crea los grupos y permisos necesarios """
    create_roles()
    session.flash = T("Bienvenido a Web2py Admin plus")
    redirect(URL('index'))


@auth.requires_login()
def index():
    grid_table = 6
    data = {}
    buscar = request.vars.search
    # Patrones de busqueda
    tablas = [tab for tab in tables if str(buscar) in tab]
    if buscar != None:
        for table in tablas:
            if auth.has_permission('read', table):
               data[table] = db(db[table]).count()
    else:
        for table in tables:
            if auth.has_permission('read', table):
                data[table] = db(db[table]).count()
    return dict(data=data, grid_table=grid_table)



def handle_delete(table, id):
    if not id:
        return

    if id:
        id_arg = id
        db[table][id] or error()

    session.ids = id

    redirect(URL('confirm_delete', args=[table, id_arg]))


@auth.requires_permission('delete', request.args(0))
def delete():
    table, row = validate(request.args(0))
    handle_delete(table, request.args[-1])


@auth.requires_permission('delete', request.args(0))
def confirm_delete():
    table, dummy = validate(request.args(0), request.args(1))
    id = session.ids
    form = FORM()

    if form.accepts(request.vars, _id="popup-validation", _class='form-horizontal', \
                    formname='delete_confirmation'):
        if id:
            row = db[table][id] or error()
            del db[table][id]
            session.flash = T('%s %s successfully deleted' % (singular(table), id))

        redirect(request.env.http_referrer or URL('list', args=table))

    return dict(table=table,
                ids=id,
                form=form,
                row=dummy)


@auth.requires_permission('read', request.args(0))
def csv():
    if auth.has_membership(role=plugins.admin_plus.superuser_role):
        arg = request.args(0) or error()
        import gluon.contenttype
        response.headers['Content-Type'] = gluon.contenttype.contenttype('.csv')
        response.headers['Content-disposition'] = 'attachment; filename=table_%s.csv'  % arg
        return str(db(db[arg], ignore_common_filters=True).select())
    else:
        error()


@auth.requires_permission('read', request.args(0))
def install_csv():
    create_roles()
    session.flash = T('data uploaded')
    redirect(URL('list', args=request.args(0)))


@auth.requires_permission('read', request.args(0))
def list():
    import math

    arg = request.args(0) or error()
    optimizar =  optimizar_paginacion

    def import_csv(table, file):
        table.import_from_csv_file(file)

    table, dummy = validate(arg)

    number_of_items = db(table.id > 0).count()
    fields = [field for field in table.fields if table[field].readable and table[field].type is not 'blob']

    if optimizar_paginacion:
        """ Si la tabla contiene mas de mil registro
           No es combeniente usar la paginacion interactiva,
           ya que afecta el rendimiento
        """

        if request.vars.page:
            current_page = int(request.vars.page)
        else:
            current_page = 1

        # Sorting
        orderby = table['id']
        if request.vars.sort:
            sort_by = request.vars.sort
            sort_by in table.fields or die()

            # GAE does not allow sorting by text fields
            if request.env.web2py_runtime_gae and table[sort_by].type is 'text':
                response.flash = T("GAE does not allow sorting by text fields")
                request.vars.sort = 'id'
            else:
                orderby = table[sort_by]
        if request.vars.sort_reverse == 'true':
            orderby = ~orderby

        items_per_page = settings.items_per_page
        number_of_pages = int(math.ceil(number_of_items / float(items_per_page)))
        pages = get_pages_list(current_page, number_of_pages)
        # algoritmo de paginacion
        limitby=((current_page-1)*items_per_page,current_page*items_per_page)

        data = db(table.id > 0).select(limitby=limitby, orderby=orderby)

        # algoritmo de busqueda
        if request.vars.search:
            query_str = request.vars.search
            pages = []
            data = []
            for field in table.fields:
                if table[field].type in ('string', 'text'):
                    datas = db(table[field].like('{0}%'.format(query_str))).select(limitby=(0, 200))
                    if datas.as_list():
                        data = datas

    if not optimizar_paginacion:
       data = db(table.id > 0).select()

    csv_table = arg

    if csv_table:
        ''' Importando datos de un archivo csv '''
        formcsv = FORM(str(T('import from csv file') + " "),
                       INPUT(_type='file', _name='csvfile'),
                       INPUT(_type='hidden', _value=csv_table, _name='table'),
                       INPUT(_type='submit', _value=T('import'), _class='fa fa-paste btn btn-line btn-metis-5', \
                             _style='margin-top: 5px'))
    else:
        formcsv = None

    if formcsv and formcsv.process().accepted:
        is_csv = request.vars.csvfile.filename
        if is_csv.endswith('.csv'):
            try:
                import_csv(db[request.vars.table],
                           request.vars.csvfile.file)
                response.flash = T('data uploaded')
            except Exception as e:
                response.error = T("unable to parse csv file {0}".format(e))
            finally:
                redirect(URL('install_csv', args=arg))
        else:
            response.error = "{0} {1}".format(is_csv, T('No es un archivo csv valido'))

    return locals()


@auth.requires_permission('read', request.args(0))
def show():
    table, row = validate(request.args(0), request.args(1))

    fields = [field for field in table.fields if table[field].readable and table[field].type is not 'blob']

    return dict(table=table,
                fields=fields,
                row=row)


@auth.requires_permission('create', request.args(0))
def new():
    table, dummy = validate(request.args(0))
    refactorizar_campos(table)

    form = SQLFORM(table, submit_button=T('Agregar'), _id="popup-validation", _class='form-horizontal')

    if form.process().accepted:
        session.flash = T('%s %s successfully created.' % (singular(table), form.vars.id))
        redirect(URL('list', args=table))
    elif form.errors:
        response.error = T('Error. Please correct the issues marked in red below.')

    return dict(table=table,
                form=form)


@auth.requires_permission('update', request.args(0))
def edit():
    table, row = validate(request.args(0), request.args(1))
    refactorizar_campos(table)

    form = SQLFORM(table,
                   record=row,
                   upload=URL('download'),
                   showid=False,
                   submit_button=T('Guardar'),
                   _id="popup-validation",
                   _class='form-horizontal')

    if form.accepts(request.vars, session):
        session.flash = '%s %s successfully updated.' % (singular(table), row['id'])
        redirect(URL('list', args=table))
    elif form.errors:
        response.error = T('Error. Please correct the issues marked in red below.')

    return dict(table=table,
                row=row,
                form=form)


def download():
    return response.download(request,db)


def user():
    form=auth()
    if form.errors:
        if request.args(0) == 'profile':
            response.error = T('Error al procesar el formulario')
        else:
            response.error = T('Correo y/o clave no es valido')
    return locals()

