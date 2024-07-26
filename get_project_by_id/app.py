import json
import uuid

try:
    from utils import get_connection, authorized
except ImportError:
    from .utils import get_connection, authorized

headers_open = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
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
        if not authorized(event, ["Admins", "Users"]):
            return {
                'statusCode': 403,
                'headers': headers_open,
                'body': json.dumps({'message': 'Unauthorized'})
            }
        if "id_project" not in event["queryStringParameters"] or not event["queryStringParameters"]["id_project"]:
            return {
                'statusCode': 400,
                'headers': headers_open,
                'body': json.dumps({'message': 'id_project is required and must be a valid uuid'})
            }
        id_project = event["queryStringParameters"]["id_project"]

        try:
            uuid.UUID(id_project)
        except ValueError:
            return {
                'statusCode': 400,
                'headers': headers_open,
                'body': json.dumps({'message': 'id_project is required and must be a valid uuid'})
            }
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM projects WHERE active = 1 AND id_project = %s", (id_project,))
        projects = cursor.fetchall()
        cursor.close()
        connection.close()

        projects2 = []
        if projects:
            for project in projects:
                projects2.append({
                    "id_project": project[0],
                    "name_project": project[1],
                    "description": project[2],
                    "active": project[3]
                })

        return {
            "statusCode": 200,
            "headers": headers_open,
            "body": json.dumps(projects2),
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers_open,
            'body': json.dumps({'message': str(e)})
        }
