import pandas as pd
import websocket, json
from trade_backend.trader import CustomTimeZone
# stored_index_list

symbol = "AAPL"

# This will start when the program intiates, will not go in any function ..... it will refresh when program will be closed
# data_loader=[]
d = {'Index Title': ['Symbol', 'TraceID', 'ExchangeID', 'Price', 'TradeSize', 'Trade Condition', 'Time_UNIX',
                     'The Market(Tape)']}
# it will create a dataFrame
df = pd.DataFrame(d).set_index('Index Title')
def on_open(ws):
    print("--------------Starting The Data Collecting process----------------")
    auth_data = {
        "action": "auth",
        "params": "Zay2cQZwZfUTozLiLmyprY4Sr3uK27Vp"
    }

    ws.send(json.dumps(auth_data))

    channel_data = {
        "action": "subscribe",
        "params": f"T.{symbol}"
    }

    ws.send(json.dumps(channel_data))

d = {'Index Title': ['Symbol', 'TraceID', 'ExchangeID', 'Price', 'TradeSize', 'Trade Condition', 'Time_UNIX',
                             'The Market(Tape)']}
# it will create a dataFrame
df = pd.DataFrame(d).set_index('Index Title')

def on_message(ws, message):
    message = json.loads(message)
    print(message)
    try:
        # data_ADDING PROCESS
        new_row = {'Symbol': message[0]['ev'], 'TraceID': message[0]['i'], 'ExchangeID': message[0]['x'],
                   'Price': message[0]['p'], 'TradeSize': message[0]['s'], 'Trade Condition': message[0]['c'],
                   'Time_UNIX': message[0]['t'], 'The Market(Tape)': message[0]['z']}
        # append row to the dataframe
        print('New York Time: '+CustomTimeZone().get_tz_time_from_nano_unix(int(int(message[0]['t']))*1000000))
    except:
        pass

def on_close(ws):
    print("closed connection & Stored")


socket = 'wss://socket.polygon.io/stocks'

ws = websocket.WebSocketApp(socket, on_open=on_open, on_message=on_message, on_close=on_close)
ws.run_forever()