import unittest
from unittest.mock import patch, MagicMock
import json
from get_my_user.app import lambda_handler, get_my_user, headers_open
from get_my_user.utils import get_connection, authorized, get_jwt_claims, get_secret



class TestGetMyUser(unittest.TestCase):
    @patch('get_my_user.app.get_connection')
    @patch('get_my_user.app.authorized')
    def test_lambda_handler_unauthorized(self, mock_authorized, mock_get_connection):
        event = {'requestContext': {'authorizer': {'claims': {'cognito:groups': ['Users']}}}}
        context = {}

        mock_authorized.return_value = False

        response = lambda_handler(event, context)

        expected_response = {
            'statusCode': 403,
            'headers': headers_open,
            'body': json.dumps({'message': 'Unauthorized'})
        }

        self.assertEqual(response, expected_response)
        mock_authorized.assert_called_once_with(event, ["Admins", "Users"])
        mock_get_connection.assert_not_called()

    @patch('get_my_user.app.get_jwt_claims')
    @patch('get_my_user.app.get_my_user')
    @patch('get_my_user.app.authorized')
    def test_lambda_handler_authorized(self, mock_authorized, mock_get_my_user, mock_get_jwt_claims):
        event = {
            'requestContext': {'authorizer': {'claims': {'cognito:groups': ['Admins']}}},
            'headers': {'Authorization': 'Bearer some_token'}
        }
        context = {}

        mock_authorized.return_value = True
        mock_get_jwt_claims.return_value = {'email': 'user1@example.com'}
        mock_get_my_user.return_value = {
            "statusCode": 200,
            'headers': headers_open,
            "body": json.dumps(
                {"id_user": "1", "full_name": "User 1", "email": "user1@example.com", "password": "password",
                 "active": True, "fk_rol": "1"})
        }

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']),
                         {"id_user": "1", "full_name": "User 1", "email": "user1@example.com", "password": "password",
                          "active": True, "fk_rol": "1"})
        mock_authorized.assert_called_once_with(event, ["Admins", "Users"])
        mock_get_jwt_claims.assert_called_once_with('some_token')
        mock_get_my_user.assert_called_once_with('user1@example.com')

    @patch('get_my_user.app.get_connection')
    def test_get_my_user(self, mock_get_connection):
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = ("1", "User 1", "user1@example.com", "password", True, "1")

        response = get_my_user("user1@example.com")

        expected_body = json.dumps({
            "id_user": "1",
            "full_name": "User 1",
            "email": "user1@example.com",
            "password": "password",
            "active": True,
            "fk_rol": "1"
        })

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['body'], expected_body)
        mock_cursor.execute.assert_called_once_with("SELECT * FROM users WHERE email = %s AND active = 1 LIMIT 1", ("user1@example.com",))
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

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

    @patch('get_my_user.utils.get_secret')
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

        with patch('get_my_user.utils.get_jwt_claims', return_value={'cognito:groups': ['Admins']}):
            self.assertTrue(authorized(event, authorized_groups))

        with patch('get_my_user.utils.get_jwt_claims', return_value={'cognito:groups': ['Users']}):
            self.assertTrue(authorized(event, authorized_groups))

        with patch('get_my_user.utils.get_jwt_claims', return_value={'cognito:groups': ['Guests']}):
            self.assertFalse(authorized(event, authorized_groups))

        with patch('get_my_user.utils.get_jwt_claims', return_value=None):
            self.assertFalse(authorized(event, authorized_groups))


if __name__ == '__main__':
    unittest.main()