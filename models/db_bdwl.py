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
                Field('id_video', 'reference video'),
                Field('notes', 'string', widget=SQLFORM.widgets.text.widget))

db.define_table('reps',
                Field('level', 'integer'),
                Field('first_set', 'integer'),
                Field('second_set', 'integer'),
                Field('third_set', 'integer'))

def get_workout(trainer, client):
    return db(db.workout.id_trainer==trainer & db.workout.id_client==client).select().first()
