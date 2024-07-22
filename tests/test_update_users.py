from unittest import TestCase


class Test(TestCase):
    pass


import unittest
from unittest.mock import patch, MagicMock
from update_users.app import lambda_handler  # replace with your actual lambda file name
from utils import get_token


class TestLambdaHandler(unittest.TestCase):

    def test_lambda_handler(self):
        # Arrange
        event = {
            'body': '{"id_user": "592894f2-96fb-4ff2-a64a-03c0e6913d45", "full_name": "Javier Ramirez Juarez", "email": "tilines@yopmail.com", "password": "secret", "active": 1, "fk_rol": "b2345c67-d890-1e23-fg45-678901bc2de3"}',
            'headers': {
                'Authorization': f' Bearer {get_token()}'
            }
        }
        context = {}
        # Act
        response = lambda_handler(event, context)
        assert response['statusCode'] == 200
