import json
import unittest
from unittest.mock import patch, MagicMock, Mock

from insert_users.app import lambda_handler, insert_user, generate_temporary_password, headers_open
from insert_users.utils import get_connection, authorized, get_jwt_claims, get_secret


class TestInsertUsers(unittest.TestCase):

    @patch('insert_users.app.get_connection')
    @patch('insert_users.app.authorized')
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
        mock_authorized.assert_called_once_with(event, ["Admins"])
        mock_get_connection.assert_not_called()

    @patch('boto3.client')
    @patch('insert_users.app.insert_user')
    @patch('insert_users.app.authorized')
    def test_lambda_handler_authorized(self, mock_authorized, mock_insert_user, mock_boto3_client):
        event = {
            'requestContext': {'authorizer': {'claims': {'cognito:groups': ['Admins']}}},
            'body': json.dumps({
                'full_name': 'User 1',
                'email': 'user1@example.com',
                'fk_rol': '1',
            })
        }
        context = {}

        mock_authorized.return_value = True
        mock_insert_user.return_value = {
            'statusCode': 200,
            'headers': headers_open,
            'body': json.dumps({'message': 'User inserted successfully with id: 1'})
        }

        # Mock boto3 client
        mock_client = Mock()
        mock_boto3_client.return_value = mock_client
        mock_client.admin_create_user.return_value = None
        mock_client.admin_add_user_to_group.return_value = None

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['body'], json.dumps({'message': 'User inserted successfully with id: 1'}))
        mock_authorized.assert_called_once_with(event, ["Admins"])
        mock_insert_user.assert_called_once()

    @patch('insert_users.app.get_connection')
    def test_insert_user(self, mock_get_connection):
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        response = insert_user("1", "User 1", "user1@example.com", "password", True, "1")

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['body'], json.dumps({'message': 'User inserted successfully with id: 1'}))
        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO users (id_user, full_name, email, password, active, fk_rol) VALUES (%s, %s, %s, %s, %s, %s)",
            ("1", "User 1", "user1@example.com", "password", True, "1")
        )
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

    def test_generate_temporary_password(self):
        password = generate_temporary_password()

        has_digit = any(char.isdigit() for char in password)
        has_upper = any(char.isupper() for char in password)
        has_lower = any(char.islower() for char in password)
        has_special = any(char in '^$*.[]{}()?-"!@#%&/\\,><\':;|_~`+= ' for char in password)

        self.assertTrue(has_digit)
        self.assertTrue(has_upper)
        self.assertTrue(has_lower)
        self.assertTrue(has_special)
        self.assertGreaterEqual(len(password), 8)

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

    @patch('insert_users.utils.get_secret')
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

        with patch('insert_users.utils.get_jwt_claims', return_value={'cognito:groups': ['Admins']}):
            self.assertTrue(authorized(event, authorized_groups))

        with patch('insert_users.utils.get_jwt_claims', return_value={'cognito:groups': ['Users']}):
            self.assertTrue(authorized(event, authorized_groups))

        with patch('insert_users.utils.get_jwt_claims', return_value={'cognito:groups': ['Guests']}):
            self.assertFalse(authorized(event, authorized_groups))

        with patch('insert_users.utils.get_jwt_claims', return_value=None):
            self.assertFalse(authorized(event, authorized_groups))


if __name__ == '__main__':
    unittest.main()