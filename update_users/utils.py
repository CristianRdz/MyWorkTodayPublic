import base64

import pymysql as PyMySQL
import boto3

def get_secret():
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name="us-east-1"
    )

    get_secret_value_response = client.get_secret_value(
        SecretId="prod/myworktodaybd"
    )

    if 'SecretString' in get_secret_value_response:
        secret = get_secret_value_response['SecretString']
    else:
        secret = base64.b64decode(get_secret_value_response['SecretBinary'])
    # El secreto viene asi:
    secret = secret.replace('\"', '')
    secret = secret.replace('{', '')
    secret = secret.replace('}', '')
    secret = secret.split(',')
    secret_dict = {}
    for s in secret:
        key, value = s.split(':')
        secret_dict[key] = value
    return secret_dict
def get_connection():
    secret = get_secret()
    return PyMySQL.connect(
        host=secret["DB_HOST"],
        user=secret["DB_USER"],
        password=secret["DB_PASSWORD"],
        database=secret["DB_NAME"],
        port=int(secret["DB_PORT"]),
    )
