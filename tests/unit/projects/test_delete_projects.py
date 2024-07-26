import json
import unittest
from unittest.mock import patch, MagicMock
from delete_projects.app import lambda_handler, is_active_project, delete_project, headers_open
from delete_projects.utils import get_secret, get_connection, get_jwt_claims, authorized

class TestDeleteProjects(unittest.TestCase):

    @patch('delete_projects.app.get_connection')
    @patch('delete_projects.app.authorized')
    def test_lambda_handler_unauthorized(self, mock_authorized, mock_get_connection):
        event = {'headers': {'Authorization': 'Bearer some_token'}}
        context = {}

        mock_authorized.return_value = False

        response = lambda_handler(event, context)

        expected_response = {
            'headers': headers_open,
            'statusCode': 403,
            'body': json.dumps({'message': 'Unauthorized'})
        }

        self.assertEqual(response, expected_response)
        mock_authorized.assert_called_once_with(event, ["Admins"])
        mock_get_connection.assert_not_called()

    @patch('delete_projects.app.delete_project')
    @patch('delete_projects.app.authorized')
    def test_lambda_handler_authorized(self, mock_authorized, mock_delete_project):
        event = {
            'headers': {'Authorization': 'Bearer some_token'},
            'queryStringParameters': {'id_project': '123456789012345678901234567890123456'}
        }
        context = {}

        mock_authorized.return_value = True
        mock_delete_project.return_value = {
            'headers': headers_open,
            'statusCode': 200,
            'body': json.dumps({'message': 'Project deleted successfully with id: 123456789012345678901234567890123456'})
        }

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['body'], json.dumps({'message': 'Project deleted successfully with id: 123456789012345678901234567890123456'}))
        mock_authorized.assert_called_once_with(event, ["Admins"])
        mock_delete_project.assert_called_once()

    @patch('delete_projects.app.get_connection')
    def test_is_active_project(self, mock_get_connection):
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [1]

        active = is_active_project("123456789012345678901234567890123456")

        self.assertEqual(active, 1)
        mock_cursor.execute.assert_called_once_with("SELECT active FROM projects WHERE id_project = %s", ("123456789012345678901234567890123456",))
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch('delete_projects.app.is_active_project')
    @patch('delete_projects.app.get_connection')
    def test_delete_project(self, mock_get_connection, mock_is_active_project):
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_is_active_project.return_value = 1

        response = delete_project("123456789012345678901234567890123456")

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['body'], json.dumps({'message': 'Project deleted successfully with id: 123456789012345678901234567890123456'}))
        mock_cursor.execute.assert_called_once_with("UPDATE projects SET active = 0 WHERE id_project = %s", ("123456789012345678901234567890123456",))
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch('boto3.session.Session')
    def test_get_secret(self, mock_session):
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        mock_client.get_secret_value.return_value = {'SecretString': '{"DB_HOST":"localhost","DB_USER":"user","DB_PASSWORD":"password","DB_NAME":"database","DB_PORT":"3306"}'}

        secret = get_secret()

        self.assertEqual(secret, {"DB_HOST":"localhost","DB_USER":"user","DB_PASSWORD":"password","DB_NAME":"database","DB_PORT":"3306"})
        mock_client.get_secret_value.assert_called_once_with(SecretId="prod/myworktodaybd")

    @patch('delete_projects.utils.get_secret')
    @patch('pymysql.connect')
    def test_get_connection(self, mock_connect, mock_get_secret):
        mock_get_secret.return_value = {"DB_HOST":"localhost","DB_USER":"user","DB_PASSWORD":"password","DB_NAME":"database","DB_PORT":"3306"}

        connection = get_connection()

        self.assertIsNotNone(connection)
        mock_connect.assert_called_once_with(host="localhost", user="user", password="password", database="database", port=3306)

    def test_get_jwt_claims(self):
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        claims = get_jwt_claims(token)

        self.assertEqual(claims, {"sub":"1234567890","name":"John Doe","iat":1516239022})

    def test_authorized(self):
        event = {'headers': {'Authorization': 'Bearer some_token'}}
        authorized_groups = ["Admins", "Users"]

        with patch('delete_projects.utils.get_jwt_claims', return_value={'cognito:groups': ['Admins']}):
            self.assertTrue(authorized(event, authorized_groups))

        with patch('delete_projects.utils.get_jwt_claims', return_value={'cognito:groups': ['Users']}):
            self.assertTrue(authorized(event, authorized_groups))

        with patch('delete_projects.utils.get_jwt_claims', return_value={'cognito:groups': ['Guests']}):
            self.assertFalse(authorized(event, authorized_groups))

        with patch('delete_projects.utils.get_jwt_claims', return_value=None):
            self.assertFalse(authorized(event, authorized_groups))

if __name__ == '__main__':
    unittest.main()