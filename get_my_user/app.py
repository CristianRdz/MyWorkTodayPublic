import json
from utils import get_connection
from utils import authorized
from utils import get_jwt_claims
headers_open = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET,PUT,POST,DELETE,OPTIONS',
    }
def lambda_handler(event, context):
    try:
        if not authorized(event, ["Admins"]):
            return {
                'statusCode': 403,
                'headers': headers_open,
                'body': json.dumps({'message': 'Unauthorized'})
            }
        claims = get_jwt_claims(event)
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


