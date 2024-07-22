import requests as req
import json


def get_token():
    url = 'https://uwicx4uhsa.execute-api.us-east-1.amazonaws.com/Prod/login'
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'username': 'ivansamuel09@icloud.com',
        'password': '7qG#UQD0YPaa'
    }
    response = req.post(url, headers=headers, data=json.dumps(data))
    return response.json()['id_token']
