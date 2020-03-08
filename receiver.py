#!/usr/bin/env python

import asyncio
import websockets
import requests
import json

API_ENDPOINT_SOCRE = "http://localhost:8080/transaction-validation"
API_WEBSOCKET_TRANSACTION = "ws://localhost:8080/transaction-stream/username/"
TEAM_NAME="team1"
TEAM_PASSWORD="pass1"

def isTransactionFraudulent(transaction):
    return True

def send_value(transaction_id, is_fraudulent):
    url = API_ENDPOINT_SOCRE + "?username=" + TEAM_NAME + "&password=" + TEAM_PASSWORD
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
        await websocket.send("Hello world!")

        while True:
            # data recieved from the API
            received = json.loads(await websocket.recv())
            print(('data received', received))

            # Sending data back to the API to compute score
            for transaction in received:
                send_value(transaction['id'], True)

asyncio.get_event_loop().run_until_complete(receive_transaction())


