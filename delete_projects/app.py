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

    Parameters
    id_project CHAR(36) NOT NULL ,
     name_project TEXT NOT NULL ,
     description TEXT ,
     active BOOLEAN NOT NULL
    ----------
       """
    try:

        if not authorized(event, ["Admins"]):
            return {
                'headers': headers_open,
                'statusCode': 403,
                'body': json.dumps({'message': 'Unauthorized'})
            }
        id_project = event["queryStringParameters"]["id_project"]
        if not id_project and id_project.length() != 36:
            return {
                'headers': headers_open,
                'statusCode': 400,
                'body': json.dumps({'message': 'id_project is required and must be a valid uuid'})
            }
        return delete_project(id_project)
    except Exception as e:
        return {
            'headers': headers_open,
            'statusCode': 500,
            'body': json.dumps({'message': str(e)})
        }


def is_active_project(id_project):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT active FROM projects WHERE id_project = %s", (id_project,))
    active = cursor.fetchone()
    cursor.close()
    connection.close()
    return active[0]


def delete_project(id_project):
    if not is_active_project(id_project):
        return {
            'headers': headers_open,
            "statusCode": 400,
            "body": json.dumps({'message': "Project is already inactive with id: " + str(id_project)}),
        }
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE projects SET active = 0 WHERE id_project = %s", (id_project,))
    connection.commit()
    cursor.close()
    connection.close()
    return {
        'headers': headers_open,
        "statusCode": 200,
        "body": json.dumps({'message': "Project deleted successfully with id: " + str(id_project)}),
    }
