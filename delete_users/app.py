import json

import boto3
from botocore.exceptions import ClientError

try:
    from utils import get_connection, authorized, get_secret
except ImportError:
    from .utils import get_connection, authorized, get_secret

headers_open = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'GET,PUT,POST,DELETE,OPTIONS',
}


def lambda_handler(event, context):
    """Sample pure Lambda function

    id_user CHAR(36) NOT NULL ,
     full_name TEXT NOT NULL ,
     email TEXT NOT NULL ,
     password TEXT NOT NULL ,
     active BOOLEAN NOT NULL ,
     fk_rol CHAR(36) NOT NULL

"""
    try:
        if not authorized(event, ["Admins"]):
            return {
                'statusCode': 403,
                'headers': headers_open,
                'body': json.dumps({'message': 'Unauthorized'})
            }
        id_user = event["queryStringParameters"]["id_user"]
        if not id_user or len(id_user) != 36:
            return {
                'statusCode': 400,
                'headers': headers_open,
                'body': json.dumps({'message': 'id_user is required and must be a valid uuid'})
            }
        return delete_user(id_user)
    except KeyError:
        return {
            'statusCode': 400,
            'headers': headers_open,
            'body': json.dumps({'message': 'id_user is required and must be a valid uuid'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers_open,
            'body': json.dumps({'message': str(e)})
        }


def is_active_user(id_user):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT active FROM users WHERE id_user = %s", (id_user,))
    active = cursor.fetchone()
    cursor.close()
    connection.close()
    return active[0]


def get_user_email(id_user):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT email FROM users WHERE id_user = %s", (id_user,))
    email = cursor.fetchone()
    cursor.close()
    connection.close()
    return email[0]


def delete_user(id_user):
    if not is_active_user(id_user):
        return {
            "statusCode": 400,
            'headers': headers_open,
            "body": json.dumps({'message': "User is already inactive with id: " + id_user}),
        }
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE users SET active = 0 WHERE id_user = %s", (id_user,))
    connection.commit()
    cursor.close()
    connection.close()
    disable_cognito_user(get_user_email(id_user))

    return {
        "statusCode": 200,
        'headers': headers_open,
        "body": json.dumps({
            "message": "User deleted successfully with id: " + id_user,
        }),
    }


def disable_cognito_user(email):
    secrets = get_secret()
    client = boto3.client('cognito-idp')
    user_pool_id = secrets['POOL_ID']
    try:
        client.admin_disable_user(
            UserPoolId=user_pool_id,
            Username=email
        )

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
