import json
import unittest
from unittest.mock import patch, MagicMock
from confirm_password.app import (lambda_handler, get_secret,headers_open)
from confirm_password.utils import get_connection, get_jwt_claims, authorized, get_secret

class TestConfirmPassword(unittest.TestCase):

    @patch('confirm_password.app.get_secret')
    @patch('boto3.client')
    def test_lambda_handler(self, mock_boto3_client, mock_get_secret):
        event = {
            "body": json.dumps({
                "username": "test_user",
                "verification_code": "123456",
                "new_password": "new_password"
            })
        }
        context = MagicMock()

        mock_get_secret.return_value = {"CLIENT_ID": "test_client_id"}
        mock_boto3_client.return_value.confirm_forgot_password.return_value = "Success"

        response = lambda_handler(event, context)

        expected_response = {
            'headers': headers_open,
            'statusCode': 200,
            'body': json.dumps({"message": "Password changed successfully", "response": "Success"})
        }

        self.assertEqual(response, expected_response)
        mock_boto3_client.assert_called_once_with('cognito-idp', region_name='us-east-1')
        mock_boto3_client.return_value.confirm_forgot_password.assert_called_once_with(
            ClientId="test_client_id",
            Username="test_user",
            ConfirmationCode="123456",
            Password="new_password"
        )

    @patch('boto3.session.Session')
    def test_get_secret(self, mock_session):
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        mock_client.get_secret_value.return_value = {
            'SecretString': '{"DB_HOST":"localhost","DB_USER":"user","DB_PASSWORD":"password","DB_NAME":"database","DB_PORT":"3306"}'}

        secret = get_secret()

        self.assertEqual(secret,
                         {"DB_HOST": "localhost", "DB_USER": "user", "DB_PASSWORD": "password", "DB_NAME": "database",
                          "DB_PORT": "3306"})
        mock_client.get_secret_value.assert_called_once_with(SecretId="prod/myworktodaybd")

    @patch('confirm_password.utils.get_secret')
    @patch('pymysql.connect')
    def test_get_connection(self, mock_connect, mock_get_secret):
        mock_get_secret.return_value = {"DB_HOST": "localhost", "DB_USER": "user", "DB_PASSWORD": "password",
                                        "DB_NAME": "database", "DB_PORT": "3306"}

        connection = get_connection()

        self.assertIsNotNone(connection)
        mock_connect.assert_called_once_with(host="localhost", user="user", password="password", database="database",
                                             port=3306)

    def test_get_jwt_claims(self):
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        claims = get_jwt_claims(token)

        self.assertEqual(claims, {"sub": "1234567890", "name": "John Doe", "iat": 1516239022})

    def test_authorized(self):
        event = {'headers': {'Authorization': 'Bearer some_token'}}
        authorized_groups = ["Admins", "Users"]

        with patch('confirm_password.utils.get_jwt_claims', return_value={'cognito:groups': ['Admins']}):
            self.assertTrue(authorized(event, authorized_groups))

        with patch('confirm_password.utils.get_jwt_claims', return_value={'cognito:groups': ['Users']}):
            self.assertTrue(authorized(event, authorized_groups))

        with patch('confirm_password.utils.get_jwt_claims', return_value={'cognito:groups': ['Guests']}):
            self.assertFalse(authorized(event, authorized_groups))

        with patch('confirm_password.utils.get_jwt_claims', return_value=None):
            self.assertFalse(authorized(event, authorized_groups))

if __name__ == '__main__':
    unittest.main()