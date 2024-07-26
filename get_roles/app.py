import json

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
    id_rol CHAR(36) NOT NULL ,
     name TEXT NOT NULL ,
     active BOOLEAN NOT NULL

"""
    try:
        if not authorized(event, ["Admins"]):
            return {
                'statusCode': 403,
                'headers': headers_open,
                'body': json.dumps({'message': 'Unauthorized'})
            }
        return get_roles()
    except Exception as e:

        return {
            'statusCode': 500,
            'headers': headers_open,
            'body': json.dumps({'message': str(e)})
        }


def get_roles():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM roles WHERE active = 1")
    roles = cursor.fetchall()
    cursor.close()
    connection.close()
    list_roles = []

    for role in roles:
        list_roles.append({
            "id_rol": role[0],
            "name": role[1],
            "active": role[2]
        })

    return {
        "statusCode": 200,
        'headers': headers_open,
        "body": json.dumps(list_roles),
    }
