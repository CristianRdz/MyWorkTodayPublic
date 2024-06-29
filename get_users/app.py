import json
import cognitojwt
from utils import get_connection

USER_POOL_ID = "us-east-1_GzEBbhwsw"
APP_CLIENT_ID = "5b1dbhgjv97slqctphs8gbkqr5"


def lambda_handler(event, context):
    try:
        token = event['headers'].get('Authorization', '').replace('Bearer ', '')
        if not token:
            raise ValueError("Token is missing")

        decoded_token = decode_token(token)
        if 'cognito:groups' not in decoded_token:
            raise ValueError("Role is missing in the token")

        user_roles = decoded_token['cognito:groups']

        if 'Admins' not in user_roles:
            return {
                'statusCode': 403,
                'body': json.dumps({'message': 'Access denied'})
            }

        return get_users()
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': str(e)})
        }


def decode_token(token):
    try:
        verified_claims = cognitojwt.decode(
            token,
            region='us-east-1',  # Reemplaza con tu región
            userpool_id=USER_POOL_ID,
            app_client_id=APP_CLIENT_ID,
            testmode=False  # Cambia a True para desactivar la verificación del token (solo para pruebas)
        )
        return verified_claims
    except Exception as e:
        raise ValueError("Token validation failed: " + str(e))


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
