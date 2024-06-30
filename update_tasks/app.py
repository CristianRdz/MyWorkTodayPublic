import json
from utils import get_connection
from utils import authorized
headers_open = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET,PUT,POST,DELETE,OPTIONS',
    }
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
    try:
        if not authorized(event, ["Admins", "Users"]):
            return {
                'statusCode': 403,
                'headers': headers_open,
                'body': json.dumps({'message': 'Unauthorized'})
            }
        event = json.loads(event['body'])
        id_task = event['id_task']
        name = event['name']
        description = event['description']
        date_time_start = event['date_time_start']
        date_time_end = event['date_time_end']
        active = event['active']
        finished = event['finished']
        id_user_assigned = event['id_user_assigned']
        fk_project = event['fk_project']

        if not name or not date_time_start or not date_time_end or not id_user_assigned or not fk_project:
            return {
                'statusCode': 400,
                'headers': headers_open,
                'body': json.dumps(
                    {'message': 'name, date_time_start, date_time_end, id_user_assigned and fk_project are required'})
            }
        # the start date must be less than the end date
        if date_time_start > date_time_end:
            return {
                'statusCode': 400,
                'headers': headers_open,
                'body': json.dumps({'message': 'date_time_start must be less than date_time_end'})
            }

        return update_task(id_task, name, description, date_time_start, date_time_end, active, finished,
                           id_user_assigned,
                           fk_project)
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers_open,
            'body': json.dumps({'message': str(e)})
        }


def update_task(id_task, name, description, date_time_start, date_time_end, active, finished, id_user_assigned,
                fk_project):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE tasks SET name = %s, description = %s, date_time_start = %s, date_time_end = %s, active = %s, finished = %s, id_user_assigned = %s, fk_project = %s WHERE id_task = %s",
        (name, description, date_time_start, date_time_end, active, finished, id_user_assigned, fk_project, id_task)
    )
    connection.commit()
    cursor.close()
    connection.close()
    return {
        'statusCode': 200,
        'headers': headers_open,
        'body': json.dumps({'message': 'Task updated successfully with id: ' + str(id_task)})
    }
