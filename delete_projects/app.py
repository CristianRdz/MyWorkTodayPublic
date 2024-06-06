import json
from utils import get_connection


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    id_project CHAR(36) NOT NULL ,
     name_project TEXT NOT NULL ,
     description TEXT ,
     active BOOLEAN NOT NULL
    ----------
       """
     # i will took the id_project from the url
    id_project = event["queryStringParameters"]["id_project"]
    if not id_project and id_project.length() != 36:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'id_project is required and must be a valid uuid'})
        }
    return delete_project(id_project)


def delete_project(id_project):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE projects SET active = 0 WHERE id_project = %s", (id_project,))
    connection.commit()
    cursor.close()
    connection.close()
    return {
        "statusCode": 200,
        "body": json.dumps({'message': "Project deleted successfully with id: " + str(id_project)}),
    }
