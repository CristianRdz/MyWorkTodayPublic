import json
import unittest
from unittest.mock import patch, MagicMock
from update_projects.app import lambda_handler, update_project, headers_open
from update_projects.utils import get_secret, get_connection, get_jwt_claims, authorized

class TestUpdateProjects(unittest.TestCase):

    @patch('update_projects.app.get_connection')
    @patch('update_projects.app.authorized')
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

    @patch('update_projects.app.update_project')
    @patch('update_projects.app.authorized')
    def test_lambda_handler_authorized(self, mock_authorized, mock_update_project):
        event = {
            'requestContext': {'authorizer': {'claims': {'cognito:groups': ['Admins']}}},
            'body': json.dumps({
                'id_project': '1',
                'name_project': 'Project 1',
                'description': 'Description',
                'active': True
            })
        }
        context = {}

        mock_authorized.return_value = True
        mock_update_project.return_value = {
            'statusCode': 200,
            'headers': headers_open,
            'body': json.dumps({'message': 'Project updated successfully with id: 1'})
        }

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['body'], json.dumps({'message': 'Project updated successfully with id: 1'}))
        mock_authorized.assert_called_once_with(event, ["Admins"])
        mock_update_project.assert_called_once()

    @patch('update_projects.app.get_connection')
    def test_update_project(self, mock_get_connection):
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        response = update_project("1", "Project 1", "Description", True)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['body'], json.dumps({'message': 'Project updated successfully with id: 1'}))
        mock_cursor.execute.assert_called_once_with(
            "UPDATE projects SET name_project = %s, description = %s, active = %s WHERE id_project = %s",
            ("Project 1", "Description", True, "1")
        )
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

class TestUtils(unittest.TestCase):

    @patch('boto3.session.Session')
    def test_get_secret(self, mock_session):
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        mock_client.get_secret_value.return_value = {'SecretString': '{"DB_HOST":"localhost","DB_USER":"user","DB_PASSWORD":"password","DB_NAME":"database","DB_PORT":"3306"}'}

        secret = get_secret()

        self.assertEqual(secret, {"DB_HOST":"localhost","DB_USER":"user","DB_PASSWORD":"password","DB_NAME":"database","DB_PORT":"3306"})
        mock_client.get_secret_value.assert_called_once_with(SecretId="prod/myworktodaybd")

    @patch('update_projects.utils.get_secret')
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

        with patch('update_projects.utils.get_jwt_claims', return_value={'cognito:groups': ['Admins']}):
            self.assertTrue(authorized(event, authorized_groups))

        with patch('update_projects.utils.get_jwt_claims', return_value={'cognito:groups': ['Users']}):
            self.assertTrue(authorized(event, authorized_groups))

        with patch('update_projects.utils.get_jwt_claims', return_value={'cognito:groups': ['Guests']}):
            self.assertFalse(authorized(event, authorized_groups))

        with patch('update_projects.utils.get_jwt_claims', return_value=None):
            self.assertFalse(authorized(event, authorized_groups))

if __name__ == '__main__':
    unittest.main()