import unittest
from unittest.mock import MagicMock
from options.app import lambda_handler, headers_open

class TestLambdaHandler(unittest.TestCase):
    def test_lambda_handler(self):
        event = MagicMock()
        context = MagicMock()

        expected_response = {
            'statusCode': 200,
            'headers': headers_open,
            'body': ''
        }

        response = lambda_handler(event, context)

        self.assertEqual(response, expected_response)

if __name__ == '__main__':
    unittest.main()