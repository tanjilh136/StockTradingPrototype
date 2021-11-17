import websockets
import time
import pandas as pd
from polygon import WebSocketClient, STOCKS_CLUSTER
import json
from datetime import datetime
import sys

li = []  # ammm eta 23:59:59 second e zero kore dewa lagbe
list_dict = []
POLYGON_URI = "wss://socket.polygon.io/stocks"
POLYGON_KEY = ""


def get_iso_time_from_mili(data):
    data = int(data / 1000)
    return datetime.fromtimestamp(data).time().isoformat()

def dump_dict(list_of_dict):
    with open('data.txt', 'w') as file:
        file.write(json.dumps(list_of_dict))  # use `json.loads` to do the reverse
    print(f"SIZE OF LIST IN MEMORY WAS : {sys.getsizeof(list_of_dict)/1000}kb")


async def stream():
    async with websockets.connect(POLYGON_URI, ssl=True, ping_interval=None) as websocket:
        await websocket.send(
            '{"action":"auth","params":"' + POLYGON_KEY + '"}')
        await websocket.send(
            '{"action":"subscribe","params":"T.*"}')

        greet = await websocket.recv()
        auth = await websocket.recv()
        sub = await websocket.recv()
        print(greet, '\n', auth, '\n', sub, '\n')

        async for messages in websocket:
            message = json.loads(messages)

            # print(message)
            for i in range(0, len(message)):
                if message[i]['sym'] not in li:
                    initial_value = message[i]['p']
                    li.append(message[i]['sym'])
                    print(f"{message[i]['sym']} len = {len(li)}")
                else:
                    for j in range(0, len(list_dict)):
                        if list_dict[j]['symbol'] == message[i]['sym']:
                            initial_value = list_dict[j]['price']
                            break
                op = get_iso_time_from_mili(message[i]['t'])
                change_percentage = ((message[i]['p'] - initial_value) / initial_value) * 100

                dicto = {
                    'time': op,
                    'timestamp': message[i]['t'],
                    'price': message[i]['p'],
                    'symbol': message[i]['sym'],
                    'percentage': change_percentage
                }
                list_dict.append(dicto)
                print(len(list_dict))

import asyncio
asyncio.run(stream())
print("RUNNING")

