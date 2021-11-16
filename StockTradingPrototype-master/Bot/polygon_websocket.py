import time
import pandas as pd
from polygon import WebSocketClient, STOCKS_CLUSTER
import json
from datetime import datetime
import sys

li = []  # am eta 23:59:59 second e zero kore dewa lagbe
list_dict = []


def get_humandate_from_mili(data):
    data = int(data / 1000)
    return datetime.fromtimestamp(data).time().isoformat()


def my_custom_process_message(message):
    message = json.loads(message)

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
        op = get_humandate_from_mili(message[i]['t'])
        change_percentage = ((message[i]['p'] - initial_value) / initial_value) * 100

        dicto = {
            'time': op,
            'timestamp': message[i]['t'],
            'price': message[i]['p'],
            'symbol': message[i]['sym'],
            'percentage': change_percentage
        }
        list_dict.append(dicto)


def my_custom_error_handler(ws, error):
    print("this is my custom error handler", error)

def dump_dict(list_of_dict):
    with open('data.txt', 'w') as file:
        file.write(json.dumps(list_of_dict))  # use `json.loads` to do the reverse
    print(f"SIZE OF LIST IN MEMORY WAS : {sys.getsizeof(list_of_dict)/1000}kb")


def my_custom_close_handler(ws):
    print("Connection closed")
    print(ws)


key = 'Zay2cQZwZfUTozLiLmyprY4Sr3uK27Vp'
my_client = WebSocketClient(STOCKS_CLUSTER, key, my_custom_process_message, on_close=my_custom_close_handler)


def main():
    my_client.run_async()
    my_client.subscribe('T.*')


if __name__ == "__main__":
    main()
    time.sleep(120)
    dump_dict(list_dict)
    my_client.close_connection()
