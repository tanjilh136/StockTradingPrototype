# Run infinite with thread for second screen data
import sys

import pandas as pd
from polygon import RESTClient
import threading
import json
import requests


def get_todays_percent_change_of_symbol(symbol):
    """
    fetch todays change in percent for the given symbol name
    :param symbol: ticker name which will be queried
    :return: todaysChangePercent
    """
    p_auth = "Zay2cQZwZfUTozLiLmyprY4Sr3uK27Vp"
    query = """https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers/""" + symbol + """?&apiKey=""" + p_auth
    print(query)
    response = requests.get(query)
    json_data = json.loads(response.text)
    print(json_data)
    try:
        change = json_data["ticker"]["todaysChangePerc"]
        return change
    except:
        return None


def get_todays_percent_change_of_symbols(symbol_array, filter_growth=0):
    """
    Returns an array of todayschange percent for every symbol_array that has that data
    i.e: It wont return data for every symbol name because some symbol doesnt have that data or inactive
    :param symbol_array:
    :return: dict of {symbol} containing the percentage value
    """
    p_auth = "Zay2cQZwZfUTozLiLmyprY4Sr3uK27Vp"
    final_data = {}
    required_iteration = int(len(symbol_array) / 1000)
    left_data_will_be = len(symbol_array) - (required_iteration * 1000)

    if required_iteration == 0:
        query = """https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers?tickers="""
        values = ",".join(symbol_array) + """&apiKey=""" + p_auth
        query = query + values
        response = requests.get(query)
        json_data = json.loads(response.text)
        for ticker in json_data["tickers"]:
            if int(ticker["todaysChangePerc"]) > filter_growth:
                final_data[ticker["ticker"]] = ticker["todaysChangePerc"]
    else:
        prev_thousand = 0
        for thousand in range(1, required_iteration + 1):
            print(f"THOUSAND : {thousand}")
            query = """https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers?tickers="""
            values = ",".join(symbol_array[prev_thousand:thousand * 1000]) + """&apiKey=""" + p_auth
            query = query + values
            response = requests.get(query)
            json_data = json.loads(response.text)
            prev_thousand = thousand * 1000
            for ticker in json_data["tickers"]:
                if int(ticker["todaysChangePerc"]) > filter_growth:
                    final_data[ticker["ticker"]] = ticker["todaysChangePerc"]
        if left_data_will_be > 0:
            print("Getting rest of the data")
            query = """https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers?tickers="""
            values = ",".join(symbol_array[prev_thousand:len(symbol_array)]) + """&apiKey=""" + p_auth
            query = query + values
            response = requests.get(query)
            json_data = json.loads(response.text)
            for ticker in json_data["tickers"]:
                if int(ticker["todaysChangePerc"]) > filter_growth:
                    final_data[ticker["ticker"]] = ticker["todaysChangePerc"]
    return final_data


def calculate_top_movers():
    df1 = pd.read_csv("app_data/company_tickers_percent.csv")
    avg_ = []
    ticker = []
    percent = []
    for i in range(0, len(df1["ticker"])):
        tick = df1["ticker"][i]
        change = df1["change_percent"][i]
        try:
            dx = pd.read_csv(f"app_data/market/barset/market_barset_data{tick}.csv")
            avg = sum(dx['volume']) / len(dx['volume'])
            avg_.append(avg)
            ticker.append(tick)
            percent.append(change)
        except:
            pass

    df2 = pd.DataFrame()
    df2['ticker'] = ticker
    df2['average'] = avg_
    df2['percent'] = percent
    return df2.sort_values('percent', ascending=False)


def top_20_barset_generator():
    p_auth = "Zay2cQZwZfUTozLiLmyprY4Sr3uK27Vp"
    query = """https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/gainers?&apiKey=""" + p_auth
    response = requests.get(query)
    json_data = json.loads(response.text)
    curr_df = pd.DataFrame()
    ticker = []
    change_percent = []

    for ticker_data in json_data["tickers"]:
        if float(ticker_data["todaysChangePerc"]) >= 25:
            ticker.append(ticker_data["ticker"])
            change_percent.append(ticker_data["todaysChangePerc"])

    curr_df["ticker"] = ticker
    curr_df["change_percent"] = change_percent
    try:
        prev_df = pd.read_csv("app_data/company_tickers_percent.csv")
        if not curr_df.equals(prev_df):
            curr_df.to_csv("app_data/company_tickers_percent.csv", index=False)
    except:
        curr_df.to_csv("app_data/company_tickers_percent.csv")


def generate_barset_forever():
    """
    This function generates barsets for all symbols provided in the csv file

    :return: None
    """
    p_auth = "Zay2cQZwZfUTozLiLmyprY4Sr3uK27Vp"
    from trade_backend.trader import CustomTimeZone

    while True:
        # Exit this thread when main thread is not alive
        for thread in threading.enumerate():
            if thread.name == "MainThread":
                if not thread.is_alive():
                    sys.exit(-1)

        top_20_barset_generator()
        c_time = CustomTimeZone()
        highest_date = c_time.get_current_iso_date()
        lowest_date = c_time.reduce_n_day_from_iso_date(3, highest_date)
        dt = pd.read_csv("app_data/company_tickers_percent.csv")
        for ticker_name in dt['ticker']:
            try:
                high = []
                low = []
                open = []
                close = []
                time = []
                volume = []
                df = pd.DataFrame()

                with RESTClient(p_auth) as client:
                    resp = client.stocks_equities_aggregates(ticker_name, 1, "minute", lowest_date, highest_date)
                    for i in range(0, len(resp.results)):
                        high.append(resp.results[i]["h"])
                        low.append(resp.results[i]["l"])
                        open.append(resp.results[i]["o"])
                        close.append(resp.results[i]["c"])
                        # here 't' is in milisec, but customtimezone requires nano_sec
                        nano_time = int(int(resp.results[i]["t"]) * 1000000)
                        share_date = c_time.get_tz_date_from_nano_unix(nano_time)
                        time.append(share_date)
                        volume.append(resp.results[i]["v"])

                    df["time"] = time
                    df["high"] = high
                    df["low"] = low
                    df["open"] = open
                    df["close"] = close
                    df["volume"] = volume
                    df.to_csv(f"app_data/market/barset/market_barset_data{ticker_name}.csv", index=False)

            except Exception:
                pass

        print("Second Screen Barset Updated: Generating top movers and storing into a csv")
        calculate_top_movers().to_csv("app_data/market/updated_sorted_movers.csv", index=True)
        print("Average calculated. Calculating again")