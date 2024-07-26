import json
import boto3
from botocore.exceptions import ClientError

try:
    from utils import get_secret
except ImportError:
    from .utils import get_secret

headers_open = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'GET,PUT,POST,DELETE,OPTIONS',
}


def lambda_handler(event, __):
    secrets = get_secret()
    client = boto3.client('cognito-idp', region_name='us-east-1')
    client_id = secrets['CLIENT_ID']
    try:
        # Parsea el body del evento
        body_parameters = json.loads(event["body"])
        username = body_parameters.get('username')

        # Inicia el flujo de recuperación de contraseña
        response = client.forgot_password(
            ClientId=client_id,
            Username=username
        )

        return {
            'statusCode': 200,
            'headers': headers_open,
            'body': json.dumps({"message": "Confirmation code sent to user's email", "response": response})
        }
    except ClientError as e:
        return {
            'statusCode': 400,
            'headers': headers_open,
            'body': json.dumps({"error_message": e.response['Error']['Message']})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers_open,
            'body': json.dumps({"error_message": str(e)})
        }
