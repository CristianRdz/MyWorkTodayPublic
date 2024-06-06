import json
from utils import get_connection


def lambda_handler(event, context):
    """Sample pure Lambda function

    id_user CHAR(36) NOT NULL ,
     full_name TEXT NOT NULL ,
     email TEXT NOT NULL ,
     password TEXT NOT NULL ,
     active BOOLEAN NOT NULL ,
     fk_rol CHAR(36) NOT NULL

"""
    try:
        id_user = event["queryStringParameters"]["id_user"]
        if not id_user and id_user.length() != 36:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'id_user is required and must be a valid uuid'})
            }
        return delete_user(id_user)
    except KeyError:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'id_user is required and must be a valid uuid'})
        }


def delete_user(id_user):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE users SET active = 0 WHERE id_user = %s", (id_user,))
    connection.commit()
    cursor.close()
    connection.close()

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "User deleted successfully with id: " + id_user,
        }),
    }
