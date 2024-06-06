import json
from utils import get_connection


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    id_rol CHAR(36) NOT NULL ,
     name TEXT NOT NULL ,
     active BOOLEAN NOT NULL

"""
    # i will took the id_rol from the url
    try:
        id_rol = event["queryStringParameters"]["id_rol"]
        if not id_rol and id_rol.length() != 36:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'id_rol is required and must be a valid uuid'})
            }
        return delete_role(id_rol)
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': str(e)})
        }


def delete_role(id_rol):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE roles SET active = 0 WHERE id_rol = %s", (id_rol,))
    connection.commit()
    cursor.close()
    connection.close()
    return {
        "statusCode": 200,
        "body": json.dumps({'message': "Role deleted successfully with id: " + str(id_rol)}),
    }
