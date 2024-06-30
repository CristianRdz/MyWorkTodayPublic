import json
from utils import get_connection
from utils import authorized

headers_open = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET,PUT,POST,DELETE,OPTIONS',
    }
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
    try:
        if not authorized(event, ["Admins"]):
            return {
                'statusCode': 403,
                'headers': headers_open,
                'body': json.dumps({'message': 'Unauthorized'})
            }
        return get_tasks()
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers_open,
            'body': json.dumps({'message': str(e)})
        }



def get_tasks():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM tasks WHERE active = 1")
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
        'headers': headers_open,
        "body": json.dumps(task_list)
    }
