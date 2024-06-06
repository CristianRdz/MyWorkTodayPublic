import json
from utils import get_connection


def lambda_handler(event, context):
    """Sample pure Lambda function

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
    # i will took the id_user from the path parameters
    id_user = event["queryStringParameters"].get("id_user")
    if not id_user and id_user.length() != 36:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Invalid id_user'})
        }
    return get_tasks(id_user)


def get_tasks(id_user):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM tasks WHERE active = 1 AND id_user_assigned = %s and finished = 0", (id_user,))
    tasks = cursor.fetchall()
    cursor.close()
    connection.close()
    task_list = []
    for task in tasks:
        task_list.append({
            "id_task": task[0],
            "name": task[1],
            "description": task[2],
            "date_time_start": task[3].strftime('%Y-%m-%dT%H:%M:%S'),
            "date_time_end": task[4].strftime('%Y-%m-%dT%H:%M:%S'),
            "active": task[5],
            "finished": task[6],
            "id_user_assigned": task[7],
            "fk_project": task[8]
        })
    return {
        "statusCode": 200,
        "body": json.dumps(task_list)
    }
