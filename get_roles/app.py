import json
from utils import get_connection


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    id_rol CHAR(36) NOT NULL ,
     name TEXT NOT NULL ,
     active BOOLEAN NOT NULL

"""
    return get_roles()


def get_roles():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM roles WHERE active = 1")
    roles = cursor.fetchall()
    cursor.close()
    connection.close()
    listRoles = []

    for role in roles:
        listRoles.append({
            "id_rol": role[0],
            "name": role[1],
            "active": role[2]
        })

    return {
        "statusCode": 200,
        "body": json.dumps(listRoles),
    }
