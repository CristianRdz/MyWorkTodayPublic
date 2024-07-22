import json
import re
from utils import get_connection
from utils import authorized
from utils import get_jwt_claims

headers_open = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': '*',
        'Access-Control-Allow-Methods': 'GET,PUT,POST,DELETE,OPTIONS',
    }


def lambda_handler(event, context):
    """
    id_user CHAR(36) NOT NULL ,
     full_name TEXT NOT NULL ,
     email TEXT NOT NULL ,
     password TEXT NOT NULL ,
     fk_rol CHAR(36) NOT NULL
    """
    # generate a new uuid
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
        roles = claims['cognito:groups']
        user_email = claims['email']

        event = json.loads(event['body'])
        id_user = event['id_user']
        full_name = event['full_name']
        email = event['email']
        password = event['password']
        fk_rol = event['fk_rol']

        if not full_name or not email or not password or not fk_rol:
            return {
                'statusCode': 400,
                'headers': headers_open,
                'body': json.dumps({'message': 'full_name, email, password and fk_rol are required'})
            }

        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if not re.match(email_regex, email):
            return {
                'statusCode': 400,
                'headers': headers_open,
                'body': json.dumps({'message': 'Invalid email format'})
            }


        # Check if the user is an admin or the email matches the user's email
        if 'Admins' in roles or user_email == email:
            return update_user(id_user, full_name, email, password, fk_rol)
        else:
            return {
                'statusCode': 403,
                'headers': headers_open,
                'body': json.dumps({'message': 'Unauthorized to edit this user'})
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers_open,
            'body': json.dumps({'message': str(e)})
        }


def update_user(id_user, full_name, email, password, fk_rol):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE users SET full_name = %s, email = %s, password = %s, fk_rol = %s WHERE id_user = %s",
        (full_name, email, password, fk_rol, id_user)
    )
    connection.commit()
    cursor.close()
    connection.close()
    return {
        'statusCode': 200,
        'headers': headers_open,
        'body': json.dumps({'message': 'User updated successfully with id: ' + str(id_user)})
    }
