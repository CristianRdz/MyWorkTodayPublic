import json
from utils import get_connection
from utils import authorized

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
                'body': json.dumps({'message': 'Unauthorized'})
            }
        event = json.loads(event['body'])
        id_rol = event['id_rol'] if 'id_rol' in event else ''
        name = event['name']
        active = event['active']

        if not name:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'name is required'})
            }

        return update_role(id_rol, name, active)
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': str(e)})
        }


def update_role(id_rol, name, active):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE roles SET name = %s, active = %s WHERE id_rol = %s", (name, active, id_rol))
    connection.commit()
    cursor.close()
    connection.close()
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Role updated successfully with id: ' + str(id_rol)})
    }
