# -*- coding: utf-8 -*-
import os
import xlrd

"""
TODO:
add increment for primary
ex. 105, 115, 125
"""

def index(): return dict(message="hello from excel.py")

@auth.requires_login()
def import_excel():
    if not is_trainer():
        redirect(URL('error'))
    id_workout = request.args(0, cast=int)
    workout_file = db.workout[id_workout].excel_file
    workbook = xlrd.open_workbook(os.path.join(request.folder, 'uploads', workout_file))
    worksheet = workbook.sheet_by_name('Sheet1')
    parse_worksheet(worksheet, id_workout)
    redirect(URL('manage', 'manage_workouts'))


exercise_col=set1_col=set2_col=level_col=variance_col = 0
accessory_cols = []
accessory_sets1 = []
accessory_sets2 = []
accessory_variances = []
primary_col=primary_set1=primary_set2=primary_set3 = 0
primary_weight1=primary_weight2=primary_weight3 = 0
headers = False
current_level = 0
current_code = '@'
current_week = 0
is_primary = False
body_part = ""

def parse_worksheet(worksheet, id_workout):
    for row in range(worksheet.nrows - 1):
        if worksheet.cell_value(row, 0) == "*":
            break
        blanks = [xlrd.XL_CELL_BLANK, xlrd.XL_CELL_EMPTY]
        global headers, current_level, current_code
        global current_week
        if not all(blank in blanks for blank in worksheet.row_types(row)):
            if not headers:
                set_headers(worksheet, row)
                if not is_primary:
                    current_code = chr(ord(current_code)+1)
                headers = True
            else:
                if not is_primary:
                    current_level += 1
                    parse_row(worksheet, id_workout, row)
                else:
                    current_week += 1
                    parse_primary(worksheet, id_workout, row)
        else:
            reset_headers()

def set_headers(worksheet, row):
    global exercise_col, set1_col, set2_col, level_col, variance_col
    global accessory_cols, accessory_sets1, accessory_sets2, accessory_variances
    global is_primary, primary_col, primary_set1, primary_set2, primary_set3
    global primary_weight1, primary_weight2, primary_weight3
    global body_part
    for col in range(worksheet.ncols - 1):
        # Cell Types: 0=Empty, 1=Text, 2=Number, 3=Date, 4=Boolean, 5=Error, 6=Blank
        cell_type = worksheet.cell_type(row, col)
        if cell_type == 0 or cell_type == 6:
            continue
        cell_value = worksheet.cell_value(row, col)
        if cell_value == "Primary":
            is_primary = True
        elif cell_value == "Exercise":
            exercise_col = col
            primary_col = col
        elif cell_value == "Set 1":
            primary_set1 = col
            if set1_col == 0:
                set1_col = col
            else:
                accessory_sets1.append(col)
        elif cell_value == "Set 2":
            primary_set2 = col
            if set2_col == 0:
                set2_col = col
            else:
                accessory_sets2.append(col)
        elif cell_value == "Set 3":
            primary_set3 = col
        elif cell_value == "Level-Up":
            if level_col == 0:
                level_col = col
        elif cell_value == "Variance":
            if variance_col == 0:
                variance_col = col
            else:
                accessory_variances.append(col)
        elif cell_value == "Accessory":
            accessory_cols.append(col)
        elif cell_value == "Weight 1":
            primary_weight1 = col
        elif cell_value == "Weight 2":
            primary_weight2 = col
        elif cell_value == "Weight 3":
            primary_weight3 = col
        elif (cell_value == "Upper Push" or
              cell_value == "Upper Pull" or
              cell_value == "Lower Push" or
              cell_value == "Lower Pull" or
              cell_value == "Core"):
            body_part = cell_value

def reset_headers():
    global exercise_col, set1_col, set2_col, level_col, variance_col, headers, current_level
    global accessory_cols, accessory_sets1, accessory_sets2, accessory_lvls, accessory_variances
    global is_primary, primary_col, primary_set1, primary_set2, primary_set3, current_week
    global primary_weight1, primary_weight2, primary_weight3
    global body_part
    exercise_col=set1_col=set2_col=level_col=variance_col = 0
    accessory_cols=[]
    accessory_sets1=[]
    accessory_sets2=[]
    accessory_lvls=[]
    accessory_variances = []
    headers = False
    current_level = 0
    current_week = 0
    is_primary = False
    primary_col=primary_set1=primary_set2=primary_set3 = 0
    primary_weight1=primary_weight2=primary_weight3 = 0
    body_part = ""

"""
format:
exercise,set1,set2,level,variance
"""
def parse_row(worksheet, id_workout, row):
    values = []
    values.append(worksheet.cell_value(row, exercise_col))
    values.append(worksheet.cell_value(row, set1_col))
    values.append(worksheet.cell_value(row, set2_col))
    values.append(worksheet.cell_value(row, level_col))
    values.append(worksheet.cell_value(row, variance_col))
    values.append(False)
    values.append(None)
    id_record = create_reps(id_workout, values, 1)
    if len(accessory_cols) != 0:
        if len(accessory_cols)==0 or len(accessory_sets1)==0 or len(accessory_sets2)==0 or len(accessory_variances)==0:
            raise Exception('INDEX OUT OF RANGE')
    for col in range(len(accessory_cols)):
        values = []
        values.append(worksheet.cell_value(row, accessory_cols[col]))
        values.append(worksheet.cell_value(row, accessory_sets1[col]))
        values.append(worksheet.cell_value(row, accessory_sets2[col]))
        values.append(worksheet.cell_value(row, level_col))
        values.append(worksheet.cell_value(row, accessory_variances[col]))
        values.append(True)
        values.append(id_record)
        create_reps(id_workout, values, (col+2))

"""
format:
exercise, set1, set2, set3, week
"""
def parse_primary(worksheet, id_workout, row):
    values = []
    values.append(worksheet.cell_value(row, primary_col))
    values.append(worksheet.cell_value(row, primary_set1))
    values.append(worksheet.cell_value(row, primary_set2))
    values.append(worksheet.cell_value(row, primary_set3))
    values.append(current_week)
    values.append(worksheet.cell_value(row, primary_weight1))
    values.append(worksheet.cell_value(row, primary_weight2))
    values.append(worksheet.cell_value(row, primary_weight3))
    create_primary(id_workout, values)

def create_primary(id_workout, values):
    exercise = db.exercise(name = values[0])
    workout = db.workout[id_workout]
    if exercise:
        id_exercise = exercise.id
    weight1 = values[5]
    weight2 = values[6]
    weight3 = values[7]
    c_week = values[4]
    set1 = values[1]
    set2 = values[2]
    set3 = values[3]
    if is_number(values[1]):
        set1 = int(set1)
    if is_number(values[2]):
        set2 = int(set2)
    if is_number(values[3]):
        set3 = int(set3)
    if exercise is None:
        id_exercise = create_exercise(id_workout, values[0])
    is_current = False
    if c_week == 1:
        is_current = True
    id_record = db.primary_reps.insert(id_workout=id_workout,
                                       id_exercise=id_exercise,
                                       c_week=c_week,
                                       set1=set1,
                                       set2=set2,
                                       set3=set3,
                                       weight1=weight1,
                                       weight2=weight2,
                                       weight3=weight3,
                                       is_current=is_current)
    return id_record

def create_reps(id_workout, values, code_num):
    exercise = db.exercise(name = values[0])
    if exercise:
        id_exercise = exercise.id
    code = current_code + str(code_num)

    set1 = values[1]
    set2 = values[2]
    level_reps = values[3]
    if is_number(values[1]):
        set1 = int(set1)
    if is_number(values[2]):
        set2 = int(set2)
    if is_number(values[3]):
        level_reps = int(level_reps)

    is_current = False
    if current_level == 1 and not values[5]:
        is_current = True
    if values[6]:
        parent = db.reps[values[6]]
        if parent.is_current:
            is_current = True
    if exercise is None:
        id_exercise = create_exercise(id_workout, values[0])
    id_record = db.reps.insert(id_workout=id_workout,
                   id_exercise=id_exercise,
                   c_level=current_level,
                   code=code,
                   reps1=set1,
                   reps2=set2,
                   level_reps=level_reps,
                   is_current=is_current,
                   variance=values[4],
                   is_accessory=values[5],
                   id_parent = values[6],
                   body_part = body_part)
    return id_record

def create_exercise(id_workout, exercise_name):
    workout = db.workout[id_workout]
    author = db.auth_user[workout.id_trainer]
    db.exercise.insert(name=exercise_name, created_by=author.id)

@auth.requires_login()
def excel_guide():
    if not is_trainer():
        redirect(URL('error'))
    #TODO: change font size
    primary = URL('static', 'images/primary.png')
    reps = URL('static', 'images/reps.png')
    excel_picture = URL('static', 'images/excel.png')
    excel_example = URL('static', 'excel_example.xlsx')
    return dict(primary=primary, reps=reps, excel_picture=excel_picture, excel_example=excel_example)
