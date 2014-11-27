@auth.requires_login()
def my_workouts():
    db.workout.id_trainer.readable = False
    db.workout.id_trainer.writable = False
    db.workout.id_trainer.default = auth.user_id
    form = SQLFORM.grid(db.workout.id_trainer==auth.user_id,
                        links = [lambda row: A('Manage Exercises',
                                               _href=URL("manage_exercises",
                                                         args=[row.id]))])
    return dict(form=form)

@auth.requires_login()
def manage_exercises():
    id_workout = request.args(0, cast=int)
    exercises = (db.exercise.id_workout==id_workout)
    #Set visibility for exercise columns
    db.exercise.id_workout.readable = False
    db.exercise.id_workout.writable = False
    db.exercise.id_workout.default = id_workout
    db.exercise.id.readable = False
    form = SQLFORM.grid(exercises, args=request.args[:2],
                        links = [lambda row: A('Manage Reps',
                                               _href=URL("manage_reps",
                                                         args=[id_workout, row.id]))])
    return dict(form=form)
    """
    options = [1::20]
    level = SELECT()
    """
    """
    form = SQLFORM.smartgrid(db.exercise,
                             constraints=dict(exercise=exercises),
                             linked_tables=['reps'], args=request.args[:2])"""

@auth.requires_login()
def manage_reps():
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
    query = (db.reps.id_workout==id_workout and db.reps.id_exercise==id_exercise)
    #record = db.reps(id_workout=id_workout,id_exercise=id_exercise,levels=current_level)
    form = SQLFORM.grid(query, args=request.args[:2])
    return dict(form=form)
