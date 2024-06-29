import json

import boto3

from utils import get_connection


def lambda_handler(event, context):

    # 1. Extract and validate Cognito token
    try:
        token = event['headers']['Authorization'].split(' ')[1]
        claims = validate_cognito_token(token)
    except Exception as e:
        print(e)
        return {
            'statusCode': 401,
            'body': json.dumps({'message': 'Token de Cognito no válido'})
        }

    # 2. Apply authorization logic based on user role
    if claims['cognito:groups'] != 'Admins':
        return {
            'statusCode': 403,
            'body': json.dumps({'message': 'Acceso no autorizado para este usuario'})
        }

    # 3. If authorized, proceed with original logic
    try:
        return get_users()
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': str(e)})
        }


def validate_cognito_token(token):
    # Use boto3's Cognito Identity Provider client to validate the token
    cognito_idp = boto3.client('cognito-idp')
    try:
        # Verify the token and return the decoded claims
        claims = cognito_idp.verify_user_info(AccessToken=token)
        return claims
    except Exception as e:
        print(e)
        raise  # Re-raise the exception for proper error handling

def get_users():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE active = 1")
    users = cursor.fetchall()
    cursor.close()
    connection.close()
    user_list = []
    for user in users:
        user_list.append({
            "id_user": user[0],
            "full_name": user[1],
            "email": user[2],
            "password": user[3],
            "active": user[4],
            "fk_rol": user[5]
        })

    return {
        "statusCode": 200,
        "body": json.dumps(user_list),
    }
