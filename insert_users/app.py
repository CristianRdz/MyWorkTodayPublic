import json
import uuid
import re
from utils import get_connection


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
        event = json.loads(event['body'])
        id_user = str(uuid.uuid4())
        full_name = event['full_name']
        email = event['email']
        password = event['password']
        active = True
        fk_rol = event['fk_rol']

        if not full_name or not email or not password or not fk_rol:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'full_name, email, password and fk_rol are required'})
            }

        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if not re.match(email_regex, email):
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Invalid email format'})
            }

        return insert_user(id_user, full_name, email, password, active, fk_rol)
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': str(e)})
        }

def insert_user(id_user, full_name, email, password, active, fk_rol):
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
        'body': json.dumps({'message': 'User inserted successfully with id: ' + str(id_user)})
    }
