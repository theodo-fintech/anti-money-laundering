#!/usr/bin/env python

import asyncio
import websockets

async def hello():
    uri = "ws://localhost:8080/transaction-stream/username/team1"
    async with websockets.connect(uri) as websocket:
        await websocket.send("Hello world!")

        while True:
            received = await websocket.recv()
            print(received)

asyncio.get_event_loop().run_until_complete(hello())
