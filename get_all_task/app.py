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
    return get_tasks()



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
        "body": json.dumps(task_list)
    }
