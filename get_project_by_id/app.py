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
        if not authorized(event, ["Admins", "Users"]):
            return {
                'statusCode': 403,
                'headers': headers_open,
                'body': json.dumps({'message': 'Unauthorized'})
            }
        id_project = event["queryStringParameters"]["id_project"]

        if not id_project and id_project.length() != 36:
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
        for project in projects:
            projects.append({
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

