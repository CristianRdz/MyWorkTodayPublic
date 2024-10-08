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
    """
    id_rol CHAR(36) NOT NULL ,
     name TEXT NOT NULL ,
     active BOOLEAN NOT NULL
    """
    # generate a new uuid
    try:
        if not authorized(event, ["Admins"]):
            return {
                'statusCode': 403,
                'headers': headers_open,
                'body': json.dumps({'message': 'Unauthorized'})
            }
        event = json.loads(event['body'])
        id_rol = str(uuid.uuid4())
        name = event['name']
        active = True

        if not name:
            return {
                'statusCode': 400,
                'headers': headers_open,
                'body': json.dumps({'message': 'name is required'})
            }

        return insert_role(id_rol, name, active)
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers_open,
            'body': json.dumps({'message': str(e)})
        }


def insert_role(id_rol, name, active):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO roles (id_rol, name, active) VALUES (%s, %s, %s)", (id_rol, name, active))
    connection.commit()
    cursor.close()
    connection.close()
    return {
        'statusCode': 200,
        'headers': headers_open,
        'body': json.dumps({'message': 'Role inserted successfully with id: ' + str(id_rol)})
    }
