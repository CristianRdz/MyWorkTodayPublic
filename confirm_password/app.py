import json
import boto3
from botocore.exceptions import ClientError
from utils import get_secret

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
        verification_code = body_parameters.get('verification_code')
        new_password = body_parameters.get('new_password')

        # Confirma el código de verificación y establece la nueva contraseña
        response = client.confirm_forgot_password(
            ClientId=client_id,
            Username=username,
            ConfirmationCode=verification_code,
            Password=new_password
        )

        return {
            'headers': headers_open,
            'statusCode': 200,
            'body': json.dumps({"message": "Password changed successfully", "response": response})
        }
    except ClientError as e:
        return {
            'headers': headers_open,
            'statusCode': 400,
            'body': json.dumps({"error_message": e.response['Error']['Message']})
        }
    except Exception as e:
        return {
            'headers': headers_open,
            'statusCode': 500,
            'body': json.dumps({"error_message": str(e)})
        }
