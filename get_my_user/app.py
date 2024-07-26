import json

try:
    from utils import get_connection, authorized, get_jwt_claims
except ImportError:
    from .utils import get_connection, authorized, get_jwt_claims
headers_open = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'GET,PUT,POST,DELETE,OPTIONS',
    'HTTP/1.1 200 OK': 'HTTP/1.1 200 OK'
}


def lambda_handler(event, context):
    try:
        if not authorized(event, ["Admins", "Users"]):
            return {
                'statusCode': 403,
                'headers': headers_open,
                'body': json.dumps({'message': 'Unauthorized'})
            }
        token = event['headers']['Authorization']
        clean_token = token.replace("Bearer ", "")
        claims = get_jwt_claims(clean_token)
        email = claims['email']
        return get_my_user(email)
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers_open,
            'body': json.dumps({'message': str(e)})
        }


def get_my_user(email):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s AND active = 1 LIMIT 1", (email,))
    user = cursor.fetchone()
    cursor.close()
    connection.close()
    if user is None:
        return {
            'statusCode': 404,
            'headers': headers_open,
            'body': json.dumps({'message': 'User not found'})
        }
    return {
        'statusCode': 200,
        'headers': headers_open,
        'body': json.dumps({
            "id_user": user[0],
            "full_name": user[1],
            "email": user[2],
            "password": user[3],
            "active": user[4],
            "fk_rol": user[5]
        })
    }
