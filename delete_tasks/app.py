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
    try:
        id_task = event["queryStringParameters"]["id_task"]
        if not id_task and id_task.length() != 36:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'id_task is required and must be 36 characters'})
            }
        return delete_task(id_task)
    except KeyError:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'id_task is required and must be 36 characters'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': str(e)})
        }


def delete_task(id_task):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE tasks SET active = 0 WHERE id_task = %s", (id_task,))
    connection.commit()
    cursor.close()
    connection.close()
    return {
        "statusCode": 200,
        "body": json.dumps({'message': "Task deleted successfully with id: " + str(id_task)}),
    }
