import json
from utils import get_connection


def lambda_handler(event, context):
    """Sample pure Lambda function

    id_user CHAR(36) NOT NULL ,
     full_name TEXT NOT NULL ,
     email TEXT NOT NULL ,
     password TEXT NOT NULL ,
     active BOOLEAN NOT NULL ,
     fk_rol CHAR(36) NOT NULL

"""
    return get_users()


def get_users():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE active = 1")
    users = cursor.fetchall()
    cursor.close()
    connection.close()
    userList = []
    for user in users:
        userList.append({
            "id_user": user[0],
            "full_name": user[1],
            "email": user[2],
            "password": user[3],
            "active": user[4],
            "fk_rol": user[5]
        })

    return {
        "statusCode": 200,
        "body": json.dumps(userList),
    }
