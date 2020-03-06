#!/usr/bin/env python

import asyncio
import websockets
import requests
import json

API_ENDPOINT = "http://localhost:8080/transaction-validation"
TEAM_NAME="team1"
TEAM_PASSWORD="pass1"

def send_value(transaction_id, is_fraudulent):
    url = API_ENDPOINT + "?username=" + TEAM_NAME + "&password=" + TEAM_PASSWORD
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
    uri = "ws://localhost:8080/transaction-stream/username/" + TEAM_NAME
    async with websockets.connect(uri) as websocket:
        await websocket.send("Hello world!")

        while True:
            received = json.loads(await websocket.recv())
            # send_value(received['id'], False)

asyncio.get_event_loop().run_until_complete(receive_transaction())


