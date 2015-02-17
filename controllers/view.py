"""
View section of site aimed at providing
clients and trainers a user-friendly view
of their workouts
"""

def index(): return dict(message="hello from view.py")

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)

"""
Display table of workouts to a client or trainer
"""
@auth.requires_login()
def my_workouts():
    db.workout.id_trainer.readable = False
    db.workout.id_trainer.writable = False
    db.workout.id_trainer.default = auth.user_id
    if is_trainer():
        workouts = db(db.workout.id_trainer==auth.user_id).select()
    else:
        membership = (db.client_list.id_client==auth.user_id)
        workouts = db(membership).select(db.workout.ALL)
    return dict(workouts=workouts)

"""
Display a workout to a client or trainer
"""
@auth.requires_login()
def workout():
    id_workout = request.args(0, cast=int)
    workout = db.workout[id_workout]
    if workout.id_trainer == auth.user_id or workout.id_client == auth.user_id:
        reps = ((db.reps.id_workout==id_workout) & (db.reps.is_current==True))
        reps_exercises = (db.exercise.id == db.reps.id_exercise)
        rows = db(reps & reps_exercises).select(orderby=db.reps.code)
        primary = ((db.primary_reps.id_workout==id_workout) & (db.primary_reps.is_current==True))
        primary_exercises = (db.exercise.id == db.primary_reps.id_exercise)
        primary_row = db(primary & primary_exercises).select()
        chat_logs = db(db.chat.id_workout==id_workout).select()
        return dict(workout=workout, rows=rows, primary_row=primary_row, chat_logs=chat_logs)
    else:
        redirect(URL('error'))

@auth.requires_login()
def pass_level():
    id_workout = request.args(0, cast=int)
    code = request.args(1, cast=str)
    level = request.args(2, cast=int)
    level_up = request.args(3)
    record = db.reps(id_workout=id_workout, code=code, c_level=level)
    if record is None:
        response.flash = "Error: record not found"
    else:
        record.update_record(level_up=level_up)
        create_level_message(id_workout, code, level)
        response.flash = "Request sent"

@auth.requires_login()
def create_level_message(id_workout, code, level):
    reps = db.reps(id_workout=id_workout, code=code, c_level=level)
    exercise = db.exercise[reps.id_exercise]
    new_level = level+1

    workout = db.workout[id_workout]
    id_trainer = workout.id_trainer
    client = db.auth_user[workout.id_client]
    if client is None:
        response.flash = "Error: client not found"
    else:
        message = ('{0} {1} ({2}) would like to level up in workout "{3}" on exercise {4} (level: {5}, code: {6})'
                   .format(client.first_name, client.last_name, client.email,
                           workout.name, exercise.name, level, code))
        db.queue.insert(id_trainer=id_trainer,
                        id_workout=id_workout,
                        id_reps=reps.id,
                        new_level=new_level,
                        queue_message=message)

"""
Display information for an exercise to a user
"""
@auth.requires_login()
def exercise():
    id_exercise = request.args(0, cast=int)
    exercise = db.exercise[id_exercise]
    author = db.auth_user[exercise.created_by]
    video = exercise.video
    if video:
        import urlparse
        url_data = urlparse.urlparse(video)
        query = urlparse.parse_qs(url_data.query)
        video = query["v"][0]
    return dict(exercise=exercise, author=author, video=video)

"""
Client view for adding feedback for a particular workout
"""
@auth.requires_login()
def add_feedback():
    id_workout = request.args(0, cast=int)
    workout = db.workout[id_workout]
    db.feedback.id_workout.readable = False
    db.feedback.id_workout.writable = False
    db.feedback.id_workout.default = id_workout
    form = SQLFORM(db.feedback, args=request.args[:1])
    form.element(_type='submit')['_style']="color:white; background:blue; font-weight:bold"
    if form.process().accepted:
       session.flash = 'Feedback submitted'
       redirect(URL('my_workouts'))
    elif form.errors:
       response.flash = 'Feedback form cannot be empty'
    return dict(form=form, workout=workout)

@auth.requires_login()
def export_workout():
    rows = db(db.workout.id).select()
    stuff = rows.export_to_csv_file(open('test.csv', 'wb'))

@auth.requires_login()
def increase_week():
    id_primary = request.args(0, cast=int)
    primary = db.primary_reps[id_primary]
    workout = db.workout(id = primary.id_workout)
    if not workout:
        redirect(URL('error'))
    current_week = primary.c_week
    next_record = db.primary_reps(id_workout = workout.id, c_week = current_week + 1)
    if next_record:
        primary.update_record(is_current = False)
        next_record.update_record(is_current = True)
        session.flash = 'Week increased'
        redirect(URL('workout', args=[workout.id]))
    else:
        session.flash = 'Next week not available'
        redirect(URL('workout', args=[workout.id]))

@auth.requires_login()
def decrease_week():
    id_primary = request.args(0, cast=int)
    primary = db.primary_reps[id_primary]
    workout = db.workout(id = primary.id_workout)
    if not workout:
        redirect(URL('error'))
    current_week = primary.c_week
    next_record = db.primary_reps(id_workout = workout.id, c_week = current_week - 1)
    if next_record:
        primary.update_record(is_current = False)
        next_record.update_record(is_current = True)
        session.flash = 'Week decreased'
        redirect(URL('workout', args=[workout.id]))
    else:
        session.flash = 'Previous week not available'
        redirect(URL('workout', args=[workout.id]))

"""
Display a report of a workout to a client
"""
@auth.requires_login()
def reports():
    workouts = db(db.workout.id_client==auth.user_id).select()
    if not workouts:
        workouts = db(db.workout.id_trainer==auth.user_id).select()
    data = [['Upper Pull','Upper Push','Lower Pull', 'Lower Push', 'Core']]
    for workout in workouts:
        data.append([get_upper_pull(workout.id),
                     get_upper_push(workout.id),
                     get_lower_pull(workout.id),
                     get_lower_push(workout.id),
                     get_core(workout.id)])
    return dict(workouts=workouts, data=data)

@auth.requires_login()
def get_report_data():
    workout = db.workout[request.args(0, cast=int)]
    data = [['Exercise Type', 'Level']]
    data.append(["Upper Pull", get_upper_pull(workout.id)])
    data.append(["Upper Push", get_upper_push(workout.id)])
    data.append(["Lower Pull", get_lower_pull(workout.id)])
    data.append(["Lower Push", get_lower_push(workout.id)])
    data.append(["Core", get_core(workout.id)])
    return dict(data=data)

def get_upper_pull(id_workout):
    record = db.reps(id_workout=id_workout, is_current=True, body_part="Upper Pull")
    if record:
        return int(record.c_level)
    return None

def get_upper_push(id_workout):
    record = db.reps(id_workout=id_workout, is_current=True, body_part="Upper Push")
    if record:
        return int(record.c_level)
    return None

def get_lower_pull(id_workout):
    record = db.reps(id_workout=id_workout, is_current=True, body_part="Lower Pull")
    if record:
        return int(record.c_level)
    return None

def get_lower_push(id_workout):
    record = db.reps(id_workout=id_workout, is_current=True, body_part="Lower Push")
    if record:
        return int(record.c_level)
    return None

def get_core(id_workout):
    record = db.reps(id_workout=id_workout, is_current=True, body_part="Core")
    if record:
        return int(record.c_level)
    return None

def create_message():
    user = db.auth_user[int(request.vars.id_user)]
    chat_message = user.first_name + ": " +request.vars.new_message
    try:
        db.chat.insert(id_workout=int(request.vars.id_workout), chat_message=chat_message, id_sender=user.id)
    except Exception, e:
        print str(e)
        return "jQuery('#messages').append(%s);" % repr(chat_message + "Message not sent.<br/>")
    return "jQuery('#messages').append(%s);" % repr(chat_message + "<br/>")
