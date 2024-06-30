import json
from utils import get_connection
from utils import authorized

def lambda_handler(event, context):
    try:
        if not authorized(event, ["Admins"]):
            return {
                'statusCode': 403,
                'body': json.dumps({'message': 'Unauthorized'})
            }
        return get_users()
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': str(e)})
        }


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
