"""
Management section of site aimed at providing
trainers the tools they need to create personal
workouts for their clients
"""

"""
User interface for managing workouts
"""
@auth.requires_login()
def my_workouts():
    if not is_trainer():
        redirect(URL('error'))
    db.workout.id_trainer.readable = False
    db.workout.id_trainer.writable = False
    db.workout.id_trainer.default = auth.user_id
    form = SQLFORM.grid(db.workout.id_trainer==auth.user_id,
                        links = [lambda row: A('Exercises',
                                               _href=URL("workout_exercises",
                                                         args=[row.id])),
                                 lambda row: A('Add Clients',
                                               _href=URL("add_clients",
                                                         args=[row.id]))])
    return dict(form=form)

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
User interface to add or remove exercises from a workout
"""
@auth.requires_login()
def workout_exercises():
    id_workout = request.args(0, cast=int)
    if not owns_workout(id_workout):
        redirect(URL('error'))
    exercises = db((db.exercise.id==db.workout_exercises.id_exercise)&
                   (db.workout_exercises.id_workout==id_workout)
                   ).select(db.exercise.ALL)
    form = FORM(INPUT(_name='keyword', requires=IS_NOT_EMPTY()),
                INPUT(_type='submit', _style="vertical-align:top"),
                _method='GET')
    records = db(db.exercise).select(limitby=(0, 15))
    """
    TODO: add exercise tags to query
    """
    if form.accepts(request.get_vars):
        query = db.exercise.name.contains(form.vars.keyword)
        query = query|db.exercise.notes.contains(form.vars.keyword)
        records = db(query).select(db.exercise.ALL)
    return dict(exercises=exercises, id_workout=id_workout, form=form, records=records)

"""
Allows a trainer to add a client to a workout
"""
@auth.requires_login()
def add_clients():
    id_workout = request.args(0, cast=int)
    if not owns_workout(id_workout):
        redirect(URL('error'))
    workouts = (id_workout==db.workout.id)
    users = (db.auth_user.role=="Client")
    records = db(users & workouts).select(db.auth_user.ALL, limitby=(0, 15))

    form = FORM(INPUT(_name='keyword', requires=IS_NOT_EMPTY()),
                INPUT(_type='submit', _style="vertical-align:top"),
                _method='GET')
    """
    TODO
    -allow for first + last name query ex. 'John Smith'
    """
    if form.accepts(request.get_vars):
        query = db.auth_user.first_name.contains(form.vars.keyword)
        query = query|db.auth_user.last_name.contains(form.vars.keyword)
        query = query|db.auth_user.email.contains(form.vars.keyword)
        records = db(query & users & workouts).select(db.auth_user.ALL)
    return dict(form=form, records=records, id_workout=id_workout)

"""
Changes the membership status of a client in a workout
"""
@auth.requires_login()
def modify_membership():
    id_workout = request.args(0, cast=int)
    if not owns_workout(id_workout):
        redirect(URL('error'))
    id_client = request.args(1,cast=int)
    if id_client == 0:
        users = db(db.auth_user).select()
        for user in users:
                add_member(id_workout, user.id)
        redirect(URL('add_clients', args=id_workout))
    elif id_client == -1:
        users = db(db.auth_user).select()
        for user in users:
                remove_member(id_workout, user.id)
        redirect(URL('add_clients', args=id_workout))
    else:
        deleted = remove_member(id_workout, id_client)
        if deleted==0:
            add_member(id_workout, id_client)
            return 'Remove Client'
        else:
            return 'Add Client'

"""
Adds a client to a workout
"""
@auth.requires_login()
def add_member(id_workout, id_client):
    if not owns_workout(id_workout):
        redirect(URL('error'))
    db.membership.insert(id_workout=id_workout,
                         id_client=id_client)

"""
Removes a client from a workout
"""
@auth.requires_login()
def remove_member(id_workout, id_client):
    if not owns_workout(id_workout):
        redirect(URL('error'))
    return db((db.membership.id_workout==id_workout)&
       (db.membership.id_client==id_client)).delete()

"""
Interface to manage reps for an exercise in a workout.
Each record is unique based on the combination of
(workout id, exercise id, user id, and level).
Users can have a record for each sequential level
"""
@auth.requires_login()
def manage_reps():
    id_workout = request.args(0, cast=int)
    if not owns_workout(id_workout):
        redirect(URL('error'))
    id_exercise = request.args(1, cast=int)
    #Set visibility for reps columns
    db.reps.id_exercise.readable = False
    db.reps.id_exercise.writable = False
    db.reps.id_exercise.default = id_exercise
    db.reps.id_workout.readable = False
    db.reps.id_workout.writable = False
    db.reps.id_workout.default = id_workout
    db.reps.id.readable = False
    members = ((db.membership.id_client==db.auth_user.id)&
               (db.membership.id_workout==id_workout))
    db.reps.id_client.requires = IS_IN_DB(db(members),
                                          db.auth_user.id,
                                          '%(first_name)s %(last_name)s (%(id)s)')

    workouts = (db.reps.id_workout==id_workout)
    exercises = (db.reps.id_exercise==id_exercise)
    session.id_workout=id_workout
    session.id_exercise=id_exercise
    form = SQLFORM.grid(workouts & exercises, oncreate=remove_level, args=request.args[:2])
    return dict(form=form, id_workout=id_workout)

"""
Deletes a (reps) record for a user based on input level
"""
@auth.requires_login()
def remove_level(form):
    print form.vars
    record = level_record(session.id_workout,
                          session.id_exercise,
                          form.vars.id_client,
                          form.vars.c_level)
    db((db.reps.id_workout==session.id_workout)&
       (db.reps.id_exercise==session.id_exercise)&
       (db.reps.id_client==form.vars.id_client)&
       (db.reps.c_level==form.vars.c_level)&
       (db.reps.id!=form.vars.id)).delete()


"""
Changes the membership status of a exercise in a workout
"""
@auth.requires_login()
def modify_exercise_list():
    id_workout = request.args(0, cast=int)
    id_exercise = request.args(1,cast=int)
    deleted = remove_exercise(id_workout, id_exercise)
    if deleted==0:
        add_exercise(id_workout, id_exercise)
    redirect(URL('workout_exercises', args=id_workout))

"""
Adds an exercise to a workout
"""
@auth.requires_login()
def add_exercise(id_workout, id_exercise):
    db.workout_exercises.insert(id_workout=id_workout,
                                id_exercise=id_exercise)

"""
Removes an exercise from a workout
"""
@auth.requires_login()
def remove_exercise(id_workout, id_exercise):
    return db((db.workout_exercises.id_workout==id_workout)&
              (db.workout_exercises.id_exercise==id_exercise)
              ).delete()

"""
TODO
-display list of queued items of users requesting to level up
-allows trainer to approve items (changes current level of reps and removes item from the queue)
"""
def my_queue():
    return dict()
