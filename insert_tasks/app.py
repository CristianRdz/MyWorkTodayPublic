import json
import uuid
from utils import get_connection
from utils import authorized


def lambda_handler(event, context):
    """
    id_task CHAR(36) NOT NULL ,
     name TEXT NOT NULL ,
     description TEXT ,
     date_time_start DATETIME(3) NOT NULL ,
     date_time_end DATETIME(3) NOT NULL ,
     active BOOLEAN NOT NULL ,
     finished BOOLEAN NOT NULL ,
     id_user_assigned CHAR(36) NOT NULL ,
     fk_project CHAR(36) NOT NULL
    """
    # generate a new uuid
    try:
        if not authorized(event, ["Admins"]):
            return {
                'statusCode': 403,
                'body': json.dumps({'message': 'Unauthorized'})
            }
        event = json.loads(event['body'])
        id_task = str(uuid.uuid4())
        name = event['name']
        description = event['description']
        date_time_start = event['date_time_start']
        date_time_end = event['date_time_end']
        active = True
        finished = False
        id_user_assigned = event['id_user_assigned']
        fk_project = event['fk_project']

        if not name or not date_time_start or not date_time_end or not id_user_assigned or not fk_project:
            return {
                'statusCode': 400,
                'body': json.dumps(
                    {'message': 'name, date_time_start, date_time_end, id_user_assigned and fk_project are required'})
            }
        # the start date must be less than the end date
        if date_time_start > date_time_end:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'date_time_start must be less than date_time_end'})
            }

        return insert_task(id_task, name, description, date_time_start, date_time_end, active, finished,
                           id_user_assigned,
                           fk_project)
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': str(e)})
        }

def is_available(id_user_assigned, date_time_start, date_time_end):
    connection = get_connection()
    cursor = connection.cursor()
    # Check if the user exists
    cursor.execute("SELECT * FROM users WHERE id_user = %s", (id_user_assigned,))
    user = cursor.fetchone()
    if user is None:
        cursor.close()
        connection.close()
        return False
    # Check if the user has any tasks in the given time interval
    cursor.execute(
        "SELECT * FROM tasks WHERE active = 1 AND id_user_assigned = %s AND ((date_time_start <= %s AND date_time_end >= %s) OR (date_time_start <= %s AND date_time_end >= %s) OR (date_time_start >= %s AND date_time_end <= %s))",
        (id_user_assigned, date_time_start, date_time_start, date_time_end, date_time_end, date_time_start, date_time_end)
    )
    tasks = cursor.fetchall()
    cursor.close()
    connection.close()
    # If the user has any tasks in the given time interval, return False
    if tasks:
        return False
    # Otherwise, return True
    return True

def insert_task(id_task, name, description, date_time_start, date_time_end, active, finished, id_user_assigned,
                fk_project):
    availability = is_available(id_user_assigned, date_time_start, date_time_end)
    if not availability:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'The user is not available in the given time interval'})
        }
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO tasks (id_task, name, description, date_time_start, date_time_end, active, finished, id_user_assigned, fk_project) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (id_task, name, description, date_time_start, date_time_end, active, finished, id_user_assigned, fk_project)
    )
    connection.commit()
    cursor.close()
    connection.close()
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Task inserted successfully with id: ' + str(id_task)})
    }


# Path: insert_tasks/requirements.txt



