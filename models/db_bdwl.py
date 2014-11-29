trainer = (db.auth_user.role == "Trainer")
client = (db.auth_user.role == "Client")
db.define_table('workout',
                Field('name', 'string', requires=IS_NOT_EMPTY()),
                Field('id_trainer', 'reference auth_user',
                      default=auth.user_id),
                Field('notes', 'string', widget=SQLFORM.widgets.text.widget))

db.define_table('membership',
                Field('id_workout', 'reference workout'),
                Field('id_client', 'reference auth_user'))

db.define_table('video',
                Field('video_file', 'upload'))

db.define_table('exercise',
                Field('name', 'string', requires=IS_NOT_EMPTY()),
                Field('video_file', 'upload'),
                Field('notes', 'string', widget=SQLFORM.widgets.text.widget),
                Field('tags', 'string'),
                Field('created_by', 'reference auth_user', default=auth.user_id))

db.define_table('workout_exercises',
                Field('id_workout', 'reference workout', requires=IS_IN_DB(db, 'workout.id', '%(name)s')),
                Field('id_exercise', 'reference exercise', requires=IS_IN_DB(db, 'exercise.id', '%(name)s')))

db.define_table('reps',
                Field('id_exercise', 'reference exercise', requires=IS_NOT_EMPTY()),
                Field('id_workout', 'reference workout', requires=IS_NOT_EMPTY()),
                Field('id_client', 'reference auth_user'),
                Field('c_level', 'integer'),
                Field('set1', 'integer'),
                Field('set2', 'integer'),
                Field('set3', 'integer'),
                Field('weight1', 'integer'),
                Field('weight2', 'integer'),
                Field('weight3', 'integer'),
                Field('level_up', 'boolean'),
                Field('is_current', 'boolean'),
                plural='Reps')

db.define_table('levels',
                Field('id_client', 'reference auth_user'),
                Field('id_exercise', 'reference exercise'),
                Field('c_level', requires=IS_INT_IN_RANGE(0,10)))

"""
TODO
-add trainer queue table
-add feedback feature
"""

def is_member(id_workout, id_client):
    return db.membership(id_workout=id_workout,
                         id_client=id_client)

def in_workout(id_workout, id_exercise):
    return db.workout_exercises(id_workout=id_workout,
                     id_exercise=id_exercise)

def level_record(id_workout, id_exercise, id_client, c_level):
    print id_workout, id_exercise, id_client, c_level
    return db.reps(id_workout=id_workout, id_exercise=id_exercise, id_client=id_client, c_level=c_level)

def owns_workout(id_workout):
    return db.workout(id=id_workout,
                      id_trainer=auth.user_id)

def is_trainer():
    record = db.workout(id_trainer=auth.user_id)
    if record is None:
        return False
    return True
