import pymysql as PyMySQL
import boto3
import base64
import json


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


def get_jwt_claims(token):
    try:
        # 1. Dividir el token en sus partes (header, payload, signature)
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Token JWT inválido")

        # 2. Decodificar el payload (segunda parte) desde Base64
        payload_encoded = parts[1]
        payload_decoded = base64.b64decode(payload_encoded + "==")  # Se agrega padding si es necesario
        claims = json.loads(payload_decoded)

        return claims

    except (ValueError, json.JSONDecodeError) as e:
        print(f"Error al decodificar el token: {e}")
        return None


def authorized(event, authorized_groups):
    token = event['headers']['Authorization']
    clean_token = token.replace("Bearer ", "")
    claims = get_jwt_claims(clean_token)
    if claims is None:
        return False
    if 'cognito:groups' not in claims:
        return False
    for group in authorized_groups:
        if group in claims['cognito:groups']:
            return True
    return False
