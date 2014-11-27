# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - api is an example of Hypermedia API support and access control
#########################################################################

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    response.flash = T("Welcome to web2py!")
    return dict(message=T('Hello World'))


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_login() 
def api():
    """
    this is example of API with access control
    WEB2PY provides Hypermedia API (Collection+JSON) Experimental
    """
    from gluon.contrib.hypermedia import Collection
    rules = {
        '<tablename>': {'GET':{},'POST':{},'PUT':{},'DELETE':{}},
        }
    return Collection(db).process(request,response,rules)

@auth.requires_login()
def my_workouts():
    form = SQLFORM.grid(db.workout.id_trainer==auth.user_id,
                        links = [lambda row: A('Manage Workout',
                                               _href=URL("manage_workout",
                                                         args=[row.id]))])
    return dict(form=form)

@auth.requires_login()
def manage_workout():
    id_workout = request.args(0, cast=int)
    workout = (db.workout.id==id_workout)
    form = SQLFORM.grid(workout, args=request.args[:1],
                        links = [lambda row: A('Manage Exercises',
                                   _href=URL("manage_exercises",
                                             args=[id_workout, row.id]))])
    return dict(form=form)

@auth.requires_login()
def manage_exercises():
    id_workout = request.args(0, cast=int)
    id_exercise = request.args(1, cast=int)
    exercises = (db.exercise.id_workout==id_workout)
    #Set visibility for exercise columns
    db.exercise.id_workout.readable = False
    db.exercise.id_workout.writable = False
    db.exercise.id_workout.default = id_workout
    db.exercise.id.readable = False
    form = SQLFORM.grid(db.exercise, args=request.args[:2],
                        links = [lambda row: A('Edit Reps',
                                               _href=URL("edit_reps",
                                                         args=[id_workout, id_exercise]))])
    """
    form = SQLFORM.smartgrid(db.exercise,
                             constraints=dict(exercise=exercises),
                             linked_tables=['reps'], args=request.args[:2])"""
    return dict(form=form)

@auth.requires_login()
def edit_reps():
    id_workout = request.args(0, cast=int)
    id_exercise = request.args(1, cast=int)
    #Set visibility for reps columns
    db.reps.id_exercise.readable = False
    db.reps.id_exercise.writable = False
    db.reps.id_exercise.default = id_exercise
    db.reps.id_workout.readable = False
    db.reps.id_workout.writable = False
    db.reps.id_workout.default = id_workout
    db.reps.id.readable = False
    record = db.reps(id_workout=id_workout,id_exercise=id_exercise)
    form = SQLFORM(db.reps, record)
    return dict(form=form)


@auth.requires_login()
def new_workout():
    db.workout.id_trainer.readable = False
    db.workout.id_trainer.writable = False
    form = SQLFORM(db.workout)
    if form.process().accepted:
        session.flash = 'New workout created'
        redirect(URL('my_workouts'))
    return locals()

@auth.requires_login()
def add_exercise():
    """
    requirements:
    create new or choose exercise
    add level, sets, and reps
    """
