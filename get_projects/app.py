import json
from utils import get_connection


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    id_project CHAR(36) NOT NULL ,
     name_project TEXT NOT NULL ,
     description TEXT ,
     active BOOLEAN NOT NULL
    ----------

"""
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM projects WHERE active = 1 ORDER BY name_project")
    projects = cursor.fetchall()
    cursor.close()
    connection.close()

    projec_list = []
    for project in projects:
        projec_list.append({
            "id_project": project[0],
            "name_project": project[1],
            "description": project[2],
            "active": project[3]
        })

    return {
        "statusCode": 200,
        "body": json.dumps(projec_list),
    }
