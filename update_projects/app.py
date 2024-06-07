import json
from utils import get_connection


def lambda_handler(event, context):
    """
    id_project CHAR(36) NOT NULL ,
     name_project TEXT NOT NULL ,
     description TEXT ,
     active BOOLEAN NOT NULL
    """
    try:
        event = json.loads(event['body'])
        id_project = event['id_project']
        name_project = event['name_project']
        description = event['description']
        active = event['active']

        if not name_project:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'name_project is required'})
            }

        return update_project(id_project, name_project, description, active)
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': str(e)})
        }


def update_project(id_project, name_project, description, active):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE projects SET name_project = %s, description = %s, active = %s WHERE id_project = %s",
        (name_project, description, active, id_project)
    )
    connection.commit()
    cursor.close()
    connection.close()
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Project updated successfully with id: ' + str(id_project)})
    }
