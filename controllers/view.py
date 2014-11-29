"""
View section of site aimed at providing
clients and trainers a user-friendly view
of their workouts
"""



def index(): return dict(message="hello from view.py")

"""
Display table of workouts to a client or trainer
"""
@auth.requires_login()
def my_workouts():
    """
    TODO
    -view for this function
    -link to each exercise
    """
    db.workout.id_trainer.readable = False
    db.workout.id_trainer.writable = False
    db.workout.id_trainer.default = auth.user_id
    if is_trainer():
        workouts = db(db.workout.id_trainer==auth.user_id).select()
    else:
        workout = (db.workout.id==db.membership.id_workout)
        membership = (db.membership.id_client==auth.user_id)
        workouts = db(workout & membership).select(db.workout.ALL)
    return dict(workouts=workouts)

def workout():
    """
    TODO
    args:id_workout
    -display table to user
    -provide link to each exercise
    -ajax to check 'level up' box
    -add to trainer queue
    -button to export to csv
    """
    return dict()

def exercise():
    """
    TODO
    args:none
    -show exercise information
    -show embedded youtube video
    """
    return dict()

def client_feedback():
    """
    TODO
    args:none
    -only accessible by trainers
    -display recent feedback from clients about a workout
    ex. 'John Smith had this to say about WorkoutA: blah blah'
    """
    return dict()
