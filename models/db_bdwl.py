trainer = (db.auth_user.role == "Trainer")
client = (db.auth_user.role == "Client")
db.define_table('workout',
                Field('name', 'string', requires=IS_NOT_EMPTY()),
                Field('id_trainer', 'reference auth_user',
                      default=auth.user_id),
                Field('id_client', 'reference auth_user'),
                Field('notes', 'string', widget=SQLFORM.widgets.text.widget),
                Field('excel_file', 'upload'))

db.define_table('exercise',
                Field('name', 'string', requires=IS_NOT_EMPTY()),
                Field('video', 'string'),
                Field('notes', 'text', widget=SQLFORM.widgets.text.widget),
                Field('tags', 'string'),
                Field('created_by', 'reference auth_user', default=auth.user_id))

db.define_table('client_list',
                Field('id_trainer', 'reference auth_user', requires=IS_NOT_EMPTY(), default=auth.user_id),
                Field('id_client', 'reference auth_user', requires=IS_NOT_EMPTY()))

clients = client & (db.client_list.id_client == db.auth_user.id)
db.workout.id_client.requires = IS_EMPTY_OR(IS_IN_DB(db(clients),
                                                     db.auth_user.id,
                                                     '%(first_name)s %(last_name)s (%(id)s)'))

db.define_table('reps',
                Field('id_workout', 'reference workout', requires=IS_NOT_EMPTY()),
                Field('id_exercise', 'reference exercise', requires=IS_IN_DB(db, 'exercise.id', '%(name)s')),
                Field('c_level', 'integer'),
                Field('code', 'string'),

                Field('reps1', 'string'),
                Field('reps2', 'string'),

                Field('level_reps', 'string'),
                Field('level_up', 'boolean'),
                Field('is_current', 'boolean'),
                Field('variance', 'string'),

                Field('is_accessory', 'boolean'),
                Field('id_parent', 'reference reps'),

                Field('body_part', 'string'),
                plural='Reps')

db.define_table('primary_reps',
                Field('id_workout', 'reference workout', requires=IS_NOT_EMPTY()),
                Field('id_exercise', 'reference exercise', requires=IS_IN_DB(db, 'exercise.id', '%(name)s')),
                Field('c_week', 'string'),
                Field('set1', 'string'),
                Field('set2', 'string'),
                Field('set3', 'string'),
                Field('weight1', 'string'),
                Field('weight2', 'string'),
                Field('weight3', 'string'),
                Field('is_current', 'boolean')
                )

db.define_table('queue',
                Field('id_trainer', 'reference auth_user'),
                Field('id_workout', 'reference workout'),
                Field('id_reps', 'reference reps'),
                Field('new_level', requires=IS_NOT_EMPTY()),
                Field('queue_message', requires=IS_NOT_EMPTY()))

db.define_table('feedback',
                Field('id_workout', 'reference workout', requires=IS_NOT_EMPTY()),
                Field('note', 'text', requires=IS_NOT_EMPTY(), represent=lambda text, row: PRE(text)))

db.define_table('images',
                Field('image', 'upload'))
"""
TODO
-add trainer queue table
-add feedback feature
"""

def getOneRm(id_client):
    record = db.auth_user[id_client]
    return record.one_rm or "0"

def process_file(id_workout):
    redirect(URL('excel', 'import_excel', args=[id_workout]))

def is_client(id_trainer, id_client):
    record = db.client_list(id_trainer=id_trainer, id_client=id_client)
    if record is None:
        return False
    return True

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
    record = db.auth_user[auth.user_id]
    if record.role == "Trainer":
        return True
    return False

def get_trainer_name(id_trainer):
    record = db.auth_user[id_trainer]
    return (record.first_name + " " + record.last_name)

def get_trainer_email(id_trainer):
    record = db.auth_user[id_trainer]
    return record.email

def get_client(id_client):
    return db.auth_user[id_client]

def calculate_oneRm(id_client, variance):
    if not is_number(variance):
        return variance
    client = db.auth_user[id_client]
    if not client:
        return 0
    oneRm = client.one_rm
    if not oneRm:
        return 0
    result = oneRm * float(variance)
    return round_to(result, 5)

def calculate_weight(id_workout, variance):
    if not is_number(variance):
        return variance
    id_client = db.workout[id_workout].id_client
    client_weight = db.auth_user[id_client].weight
    if not client_weight:
        raise Exception("Client weight has not been set")
    result = client_weight * float(variance)
    return round_to(result, 5)

def round_to(value, precision):
    return int(precision * round(float(value)/precision))

def is_number(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

site_name = "Level Train"
