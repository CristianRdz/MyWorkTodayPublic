import json
from utils import get_connection
from utils import authorized

def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    id_rol CHAR(36) NOT NULL ,
     name TEXT NOT NULL ,
     active BOOLEAN NOT NULL

"""
    try:
        if not authorized(event, ["Admins"]):
            return {
                'statusCode': 403,
                'body': json.dumps({'message': 'Unauthorized'})
            }
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

def is_active_role(id_rol):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT active FROM roles WHERE id_rol = %s", (id_rol,))
    active = cursor.fetchone()
    cursor.close()
    connection.close()
    return active[0]

def delete_role(id_rol):
    if not is_active_role(id_rol):
        return {
            "statusCode": 400,
            "body": json.dumps({'message': "Role is already inactive with id: " + str(id_rol)}),
        }
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
