#!/usr/bin/env python

import asyncio
import websockets
import requests
import json
import urllib.parse

API_HOST = "35.180.196.161"
API_PORT = "8080"
API_ENDPOINT_SCORE = "/transaction-validation"
API_WEBSOCKET_TRANSACTION = "ws://" + API_HOST + ":" + API_PORT + "/transaction-stream/username/"

TEAM_NAME="team1"
TEAM_PASSWORD="pass1"

def send_value(transaction_id, is_fraudulent):
    url = "http://" + API_HOST + ":" + API_PORT + API_ENDPOINT_SCORE
    params = {
        'username': TEAM_NAME,
        'password': TEAM_PASSWORD
    }
    queryParams = urllib.parse.urlencode(params)
    url += "?" + queryParams

    # data to be sent to api
    data = {
        'fraudulent': is_fraudulent,
        'transaction': {
            'id': transaction_id
        }
    }

    # sending post request and saving response as response object
    requests.post(url = url, json = data, )

async def receive_transaction():
    uri = API_WEBSOCKET_TRANSACTION + TEAM_NAME
    async with websockets.connect(uri) as websocket:
        while True:
            try:
                received = json.loads(await websocket.recv())
                process_transactions(received)
            except:
                print('Reconnecting')
                websocket = await websockets.connect(uri)


def process_transactions(transactions):
    # Sending data back to the API to compute score
    for transaction in transactions:
        is_fraud = is_transaction_fraudulent(transaction)
        # send_value(transaction['id'], is_fraud)

    return True;

def is_transaction_fraudulent(transaction):
    return True



if __name__== "__main__":
    asyncio.get_event_loop().run_until_complete(receive_transaction())

