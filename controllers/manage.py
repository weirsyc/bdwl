"""
Management section of site aimed at providing
trainers the tools they need to create personal
workouts for their clients
"""

def index(): return dict(message="hello from manage.py")

"""
User interface for managing workouts
"""
@auth.requires_login()
def manage_workouts():
    if not is_trainer():
        redirect(URL('error'))
    db.workout.id_trainer.readable = False
    db.workout.id_trainer.writable = False
    db.workout.id_trainer.default = auth.user_id
    form = SQLFORM.grid(db.workout.id_trainer==auth.user_id,
                        links = [lambda row: A('Manage',
                                               _href=URL("workout",
                                                         args=[row.id]))],
                        oncreate = import_excel)

    return dict(form=form)

@auth.requires_login()
def import_excel(form):
    if form.vars.excel_file:
        process_file(form.vars.id)

"""
User interface for manually customizing workouts (reps)
"""
@auth.requires_login()
def workout():
    id_workout = request.args(0, cast=int)
    if not owns_workout(id_workout):
        redirect(URL('error'))
    db.reps.id_workout.readable = False
    db.reps.id_workout.writable = False
    db.reps.id_workout.default = id_workout
    session.id_workout=id_workout
    form = SQLFORM.grid(db.reps.id_workout==id_workout,
                        args=request.args[:1],
                        onvalidation=process_new_reps)
    name = db.workout[id_workout].name
    return dict(form=form, name=name, id_workout=id_workout)

"""
User interface for manually customizing workouts (primary table)
"""
@auth.requires_login()
def primary():
    id_workout = request.args(0, cast=int)
    if not owns_workout(id_workout):
        redirect(URL('error'))
    db.primary_reps.id_workout.readable = False
    db.primary_reps.id_workout.writable = False
    db.primary_reps.id_workout.default = id_workout
    form = SQLFORM.grid(db.primary_reps.id_workout==id_workout,
                        args=request.args[:1])
    name = db.workout[id_workout].name
    return dict(form=form, name=name, id_workout=id_workout)

@auth.requires_login()
def process_new_reps(form):
    record = db.reps(id_workout=session.id_workout, code=form.vars.code, c_level=form.vars.c_level)
    if (record) is not None:
        session.flash = 'record updated'
        if not record.is_accessory:
            update_reps(record, form.vars)
        redirect(URL('manage','workout', args=[session.id_workout]))

@auth.requires_login()
def update_reps(record, form_vars):
    record.update_record(id_exercise=form_vars.id_exercise,   reps1=form_vars.reps1,
                         weight=form_vars.weight,             reps2=form_vars.reps2,
                         level_reps=form_vars.level_reps,     level_up=form_vars.level_up,
                         is_current=form_vars.is_current,     variance=form_vars.variance, 
                         is_accessory=form_vars.is_accessory)

"""
User interface for adding and removing client/trainer association
"""
@auth.requires_login()
def manage_clients():
    records = db(client).select(db.auth_user.ALL, limitby=(0, 15))

    form = FORM(INPUT(_name='keyword', requires=IS_NOT_EMPTY()),
                INPUT(_type='submit', _style="vertical-align:top"),
                _method='GET')
    if form.accepts(request.get_vars):
        query = db.auth_user.first_name.contains(form.vars.keyword)
        query = query|db.auth_user.last_name.contains(form.vars.keyword)
        query = query|db.auth_user.email.contains(form.vars.keyword)
        words = form.vars.keyword.split(" ")
        if len(words) > 1:
            query = query|(db.auth_user.first_name.contains(words[0])&
                           db.auth_user.last_name.contains(words[1]))
        records = db(query & client).select(db.auth_user.ALL)
    return dict(form=form, records=records)

"""
Changes the membership status of a client
"""
@auth.requires_login()
def modify_membership():
    id_trainer = request.args(0, cast=int)
    if not is_trainer():
        redirect(URL('error'))
    id_client = request.args(1,cast=int)
    record = db.client_list(id_trainer=id_trainer, id_client=id_client)
    if record is None:
        add_client(id_trainer, id_client)
        return 'Remove Client'
    else:
        remove_client(id_trainer, id_client)
        return 'Add Client'

"""
Adds a client membership
"""
@auth.requires_login()
def add_client(id_trainer, id_client):
    db.client_list.insert(id_trainer=id_trainer,
                         id_client=id_client)

"""
Removes a client membership
"""
@auth.requires_login()
def remove_client(id_trainer, id_client):
    return db((db.client_list.id_trainer==id_trainer)&
       (db.client_list.id_client==id_client)).delete()

"""
User interface for viewing current client/trainer relationships
"""
@auth.requires_login()
def client_list():
    clients = db((db.client_list.id_trainer==auth.user_id) &
                 (db.client_list.id_client==db.auth_user.id)
                 ).select(db.auth_user.ALL)
    return dict(clients=clients)

def setOneRm():
    record = db.auth_user[request.args(0, cast=int)]
    oneRm = request.vars.oneRm[request.args(1, cast=int)-1]
    record.update_record(one_rm=oneRm)

"""
User interface for managing exercises
"""
@auth.requires_login()
def manage_exercises():
    if not is_trainer():
        redirect(URL('error'))
    my_exercises = (db.exercise.created_by==auth.user_id)
    db.exercise.created_by.readable=False
    db.exercise.created_by.writable=False
    form = SQLFORM.grid(my_exercises)
    return dict(form=form)

"""
User interface for managing client upgrades
-displays list of queued items of users requesting to level up
-allows trainer to approve or deny items
"""
def my_queue():
    if not is_trainer():
        redirect(URL('error'))
    records = db(db.queue.id_trainer == auth.user_id).select()
    return dict(records=records)

def level_up_client():
    if not is_trainer():
        redirect(URL('error'))
    reps = db.reps[request.args(0, cast=int)]
    workout = db.workout[request.args(1, cast=int)]
    new_level = request.args(2, cast=int)
    in_workout = request.args(3, cast=bool)
    new_reps = db((db.reps.id_workout==reps.id_workout) & (db.reps.code[0]==reps.code[0]) & (db.reps.c_level==new_level)).select()
    if not new_reps:
        if in_workout:
            session.flash = "Requested level not available"
        response.flash = (("Next level not found. Please add the next level for this workout: " +
                          "{0} (level:{1}, code:{2}). Then reload this page.").format(workout.name, new_level, reps.code))
    else:
        old_reps = db((db.reps.id_workout==reps.id_workout) & (db.reps.code[0]==reps.code[0]) & (db.reps.c_level==reps.c_level)).select()
        for r in old_reps:
            r.update_record(level_up=False, is_current=False)
        for r in new_reps:
            r.update_record(level_up=False, is_current=True)
        remove_from_queue(reps.id)
    if in_workout:
        redirect(URL('view', 'workout', args=[workout.id]))

def remove_from_queue(id_reps):
    db(db.queue.id_reps == id_reps).delete()

def reset_client():
    if not is_trainer():
        redirect(URL('error'))
    reps = db.reps[request.args(0, cast=int)]
    reps.update_record(level_up=False, is_current=True)
    remove_from_queue(reps.id)

"""
User interface for viewing and removing client feedback
"""
def feedback():
    if not is_trainer():
        redirect(URL('error'))
    feedback = db((db.feedback.id_workout == db.workout.id)
                  &(db.workout.id_trainer == auth.user_id)
                  &(db.auth_user.id==db.workout.id_client)).select()
    return dict(feedback=feedback)

def delete_feedback():
    id_feedback = request.args(0, cast=int)
    deleted = db(db.feedback.id == id_feedback).delete()
    if deleted == 1:
        session.flash = "Record deleted"
        redirect(URL('feedback'))

def error():
    return dict(error="An error has occurred.")
