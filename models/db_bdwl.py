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
                Field('id_workout', 'reference workout', requires=IS_IN_DB(db, 'workout.id', '%(name)s')),
                Field('video_file', 'upload'),
                Field('notes', 'string', widget=SQLFORM.widgets.text.widget))

db.define_table('reps',
                Field('id_exercise', 'reference exercise', requires=IS_NOT_EMPTY()),
                Field('id_workout', 'reference workout', requires=IS_NOT_EMPTY()),
                Field('levels', 'integer'),
                Field('set1', 'integer'),
                Field('set2', 'integer'),
                Field('set3', 'integer'),
                Field('weight1', 'integer'),
                Field('weight2', 'integer'),
                Field('weight3', 'integer'),
                Field('user_input', 'integer'),
                plural='Reps')

def get_workout(trainer):
    return db.workout(id_trainer=trainer)
