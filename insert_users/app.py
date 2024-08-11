import json
import uuid
import re
import string
import boto3
import secrets
from botocore.exceptions import ClientError
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
    id_user CHAR(36) NOT NULL ,
     full_name TEXT NOT NULL ,
     email TEXT NOT NULL ,
     password TEXT NOT NULL ,
     active BOOLEAN NOT NULL ,
     fk_rol CHAR(36) NOT NULL
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
        id_user = str(uuid.uuid4())
        full_name = event['full_name']
        email = event['email']
        password = generate_temporary_password()
        active = True
        fk_rol = event['fk_rol']
        role = find_role(fk_rol) if find_role(fk_rol) is not None else "Users"

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

        client = boto3.client('cognito-idp', region_name='us-east-1')
        user_pool_id = "us-east-1_GzEBbhwsw"
        # Crea el usuario con correo no verificado y contraseña temporal que se envia automaticamente a su correo
        client.admin_create_user(
            UserPoolId=user_pool_id,
            Username=email,
            UserAttributes=[
                {'Name': 'email', 'Value': email},
                {'Name': 'email_verified', 'Value': 'false'},
            ],
            TemporaryPassword=password
        )

        client.admin_add_user_to_group(
            UserPoolId=user_pool_id,
            Username=email,
            GroupName=role
        )
        return insert_user(id_user, full_name, email, "secret", active, fk_rol)

    except ClientError as e:
        return {
            'statusCode': 400,
            'headers': headers_open,
            'body': json.dumps({'message': e.response['Error']['Message']})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers_open,
            'body': json.dumps({'message': str(e)})
        }


def insert_user(id_user, full_name, email, password, active, fk_rol):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO users (id_user, full_name, email, password, active, fk_rol) VALUES (%s, %s, %s, %s, %s, %s)",
            (id_user, full_name, email, password, active, fk_rol)
        )
        connection.commit()
        cursor.close()
        connection.close()
        return {
            'statusCode': 200,
            'headers': headers_open,
            'body': json.dumps({'message': 'User inserted successfully with id: ' + str(id_user)})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers_open,
            'body': json.dumps({'message': str(e)})
        }


def generate_temporary_password(length=12):
    """Genera una contraseña temporal segura"""
    special_characters = '^$*.[]{}()?-"!@#%&/\\,><\':;|_~`+= '
    characters = string.ascii_letters + string.digits + special_characters

    while True:
        # Genera una contraseña aleatoria
        password = ''.join(secrets.choice(characters) for _ in range(length))

        # Verifica los criterios
        has_digit = any(char.isdigit() for char in password)
        has_upper = any(char.isupper() for char in password)
        has_lower = any(char.islower() for char in password)
        has_special = any(char in special_characters for char in password)

        if has_digit and has_upper and has_lower and has_special and len(password) >= 8:
            return password


def find_role(fk_rol):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM roles WHERE id_rol = %s", (fk_rol,))
    role = cursor.fetchone()
    cursor.close()
    connection.close()
    return role[0] if role is not None else None