import os
from datetime import datetime, timedelta
from threading import Thread
import requests
from trade_backend.trader import CustomTimeZone
import pandas as pd
from polygon import WebSocketClient, STOCKS_CLUSTER
import json
import glob
from datetime import datetime
from trade_backend.trader import CustomTimeZone


class PolygonRealTimeTradeData:
    LAST_7_DAYS_FIRST_TIME_AND_3_TIMES_VOLATILITY_THAN_PREVIOUS_WEEK_HIGHEST_VOLATILITY = "* symbol *"
    LAST_7_DAYS_FIRST_TIME_AND_3_TIMES_VOLATILITY_THAN_PREVIOUS_WEEK_HIGHEST_VOLATILITY_HAS_NEWS = "$ **symbol** $"
    LAST_7_DAYS_FIRST_TIME = "symbol *"
    LAST_7_DAYS_FIRST_TIME_HAS_NEWS = "$ symbol * $"
    LAST_7_MORE_THAN_ONE_TIME = "symbol"
    LAST_7_MORE_THAN_ONE_TIME_HAS_NEWS = "$ symbol $"

    MIN_CHANGE_DEFAULT = 100000
    MAX_CHANGE_DEFAULT = -100000

    def __init__(self, tickers="T.*", start_fetching_at_nyt_today="15:59:59", packup_at_nyt_tomorrow="15:59:30"):
        """
        The program must not crash or stop receiving data for each 24 hrs. When the program starts it will
        Consider the first data as initial data. If it crashes, the calculation will effect the whole process
        :param tickers:
        """
        self.key = 'Zay2cQZwZfUTozLiLmyprY4Sr3uK27Vp'
        self.my_client = WebSocketClient(cluster=STOCKS_CLUSTER, auth_key=self.key,
                                         process_message=self.on_message_received,
                                         on_close=self.on_close, on_error=self.on_error)
        self.target_tickers = tickers
        self.custom_time = CustomTimeZone()
        self.all_symbols = []
        self.init_all_symbol_names_from_file()

        self.current_day_data = {}
        self.init_current_day_data()

        self.last_msg_time_sec = {}
        self.init_last_msg_time_sec()

        self.prev_week_highest_volatility = {}
        self.init_prev_week_highest_volatility_from_file()

        self.today_sms_data = []
        self.current_week_sms_data = []
        self.init_current_week_sms_data_from_file()

        self.current_day_count = self.how_many_days_elapsed() + 1
        self.start_fetching_current_day_at_new_york_time = start_fetching_at_nyt_today
        self.pack_up_current_day_at_new_york_time = packup_at_nyt_tomorrow
        self.start_at_utc_sec = 0
        self.packup_at_utc_sec = 0

        self.init_start_packup_timestamp()

    def has_news(self, symbol):
        """
        Finds out if today we have a news on specified symbol
        :param symbol:
        :return:
        """
        curr_date = self.custom_time.get_current_iso_date()
        api = f"https://api.polygon.io/v2/reference/news?limit=1&order=descending&sort=published_utc&ticker={symbol}&published_utc={curr_date}&apiKey={self.key}"
        res = requests.get(api)
        res = json.loads(res.text)
        if len(res["results"]) > 0:
            return True
        else:
            return False

    def packup_for_today(self):
        """
        1. Setup new timestamp for start and packup
        2. Dump current day day
            a. If 7 days completes redefine the previous week highest volatility
            b. Delete day1.txt to day2.txt
        3. Dump Current week sms data
        4. Initialize current day data with default value
        :return:
        """
        self.init_start_packup_timestamp()
        self.dump_current_day_data()
        self.dump_current_week_sms_data()
        self.init_current_day_data()

    def init_start_packup_timestamp(self):
        custom_time = CustomTimeZone()
        curr_year, curr_month, curr_day = custom_time.get_current_iso_date().strip().split("-")
        curr_hr, curr_min, curr_sec = self.start_fetching_current_day_at_new_york_time.strip().split(":")
        self.start_at_utc_sec = int(
            datetime(year=int(curr_year), month=int(curr_month), day=int(curr_day), hour=int(curr_hr),
                     minute=int(curr_min), second=int(curr_sec)).timestamp())

        pack_hr, pack_min, pack_sec = self.pack_up_current_day_at_new_york_time.strip().split(":")
        self.packup_at_utc_sec = int(
            (datetime(year=int(curr_year), month=int(curr_month), day=int(curr_day), hour=int(pack_hr),
                      minute=int(pack_min), second=int(pack_sec)) - timedelta(days=1)).timestamp())

    def init_current_week_sms_data_from_file(self):
        with open("week_data/current_week_sms_data.txt") as file:
            self.current_week_sms_data = json.load(file)
            print("....SMS DATA INITIALIZED FROM FILE.....")
            print(self.current_week_sms_data)

    def reset_current_week_sms_data(self):
        self.current_week_sms_data = []
        with open("week_data/current_week_sms_data.txt", "w") as file:
            file.write(json.dumps(self.current_week_sms_data))
            print("........CURRENT WEEK SMS DATA RESET SUCCESSFUL.........")
            print(self.current_week_sms_data)

    def dump_current_week_sms_data(self):
        """
        Whenever we send an sms on 20% growth, we add the symbol name in current_week_sms_data
        Use this function to make the list persistent
        :return:
        """
        with open("week_data/current_week_sms_data.txt", "w") as file:
            file.write(json.dumps(self.current_week_sms_data))
            print(".......CURRENT WEEK SMS DATA DUMPING SUCCESSFUL........")
            print(self.current_week_sms_data)

    def init_last_msg_time_sec(self, value=0):
        """
        Initialize last_msg_time_sec data with initial value
        :return:
        """
        self.last_msg_time_sec = {}
        for sym in self.all_symbols:
            self.last_msg_time_sec[sym] = value

    def how_many_days_elapsed(self):
        """
        The day_data folder contains only day files. Count of those files starting
        with text 'day' is the total day elapsed
        :return:
        """
        list_of_days = glob.glob("day_data/day*.txt")
        print("..........Day Data File Paths..........")
        print(list_of_days)
        return len(list_of_days)

    def reset_weekly_highest_volatility_file(self, value=0):
        """
        Resets the previous_week_highest_volatility.txt with initial value 0
        :return:
        """

        week_volatility = {}
        for sym in self.all_symbols:
            week_volatility[sym] = value
        with open("week_data/previous_week_highest_volatility.txt", "w") as week:
            week.write(json.dumps(week_volatility))

    def init_prev_week_highest_volatility_from_file(self):
        """
        Read highest volatility from file and initialized it into prev_week_highest_volatility
        :return:
        """
        with open("week_data/previous_week_highest_volatility.txt") as file:
            self.prev_week_highest_volatility = json.load(file)
            print("..........PREVIOUS_WEEK_VOLATILITY.............")
            print(self.prev_week_highest_volatility)

    def init_all_symbol_names_from_file(self):
        """
        Initialize all ticker symbol names from the csv file into all_symbols as list
        :return:
        """
        df = pd.read_csv("../app_data/company_tickers.csv")
        self.all_symbols = df["symbol"].to_numpy()

    def redefine_weekly_highest_volatility(self):
        """
        Find highest volatility of each symbol from day1.txt to day7.txt files and dump the highest
        volatility dictionary into the previous_week_volatility.txt file
        :return:
        """
        print("CALCULATING WEEKLY HIGHEST VOLATILITY")
        self.reset_weekly_highest_volatility_file()
        self.init_prev_week_highest_volatility_from_file()

        list_of_days = glob.glob("day_data/day*.txt")
        for day_data_path in list_of_days:
            with open(day_data_path) as file:
                day_data = json.load(file)
                # Iterate over each ticker symbol and find the largest
                # day_data and initialize it into prev_week_highest_volatility
                for sym in self.all_symbols:
                    if self.prev_week_highest_volatility[sym] < day_data[sym]["volatility"]:
                        self.prev_week_highest_volatility[sym] = day_data[sym]["volatility"]
                print(f"Successfully Analyzed file : {day_data_path}")

        # Dump calculated volatility into previous_week_highest_volatility.txt file
        with open("week_data/previous_week_highest_volatility.txt", "w") as week:
            week.write(json.dumps(self.prev_week_highest_volatility))
            print(".....SUCCESSFULLY DUMPED HIGHEST VOLATILITY OF PREV WEEK TICKERS.......")
            print(self.prev_week_highest_volatility)
            print("....Deleting Day1.txt to Day2.txt....")
            self.delete_last_days_file()

    def delete_last_days_file(self):
        """
        delete day files from day1.txt to day7.txt.
        must not face exception, otherwise bot will not work
        :return:
        """
        list_of_days = glob.glob("day_data/day*.txt")
        for day_file in list_of_days:
            try:
                os.remove(day_file)
                print(f"DELETED : {day_file}")
            except Exception as e:
                print(
                    "Day file could not be deleted, please permit deleting."
                    "Otherwise bot will not work properly")
                print(e)

    def dump_current_day_data(self):
        """
        Dump current day data into day*.txt file, so that we can calculate highest volatility
        from 7 days When total 7 days count is completed, calculate the highest volatility
        and dump it into previous_week_highest_volatility
        :return:
        """
        elapsed_day = self.how_many_days_elapsed()
        with open(f"day_data/day{elapsed_day + 1}.txt", "w") as week:
            week.write(json.dumps(self.current_day_data))
        if elapsed_day == 7:
            self.redefine_weekly_highest_volatility()

    def on_websocket_closed_dump_backup_data_on_crash(self):
        """
        When websocket is closed because of any error, this function will
        dump current_data_data into a txt file, so that it can be used later
        dump current_week_sms_data into a txt file, so that it can be used later
        :return:
        """
        print("Dump important data that need to be recovered on restart")

    def on_web_socket_open_recover_data_after_crash(self):
        """
        Recover from backup data, so that the program can continue without losing previously calculated data
        but will will not be able to fetch missing seconds data, as it was not calculated
        :return:
        """
        print("Read backup data so that bot can run smoothly")

    def init_current_day_data(self, init_price=0, min_change=100000, max_change=-100000, volatility=0):
        """
        Initialize current_day_data with initial value.
        It happens every day before starting the fetching process for each day stock data
        :return:
        """
        self.MIN_CHANGE_DEFAULT = min_change
        self.MAX_CHANGE_DEFAULT = max_change
        self.current_day_data = {}
        for symbol in self.all_symbols:
            ticker_dict = {
                "init_price": init_price,
                "min_change": min_change,
                "max_change": max_change,
                "volatility": volatility
            }
            self.current_day_data[symbol] = ticker_dict

    def start_fetching(self):
        self.my_client.run_async()
        self.my_client.subscribe(self.target_tickers)

    def on_close(self, ws):
        self.on_websocket_closed_dump_backup_data_on_crash()
        print(ws)

    def on_error(self, ws, error):
        print(f"Error Faced {error}")

    def on_message_received(self, message):
        message = json.loads(message)
        for msg in message:
            msg_time_in_sec = int(msg['t'] / 1000)  # milli to sec
            if self.last_msg_time_sec[msg["sym"]] < msg_time_in_sec:
                # Process now
                if self.packup_at_utc_sec <= msg_time_in_sec:
                    # Its time to packup
                    self.packup_for_today()  # Requires improvement on handling already received data
                else:
                    # Continue current day calculation
                    self.last_msg_time_sec[msg["sym"]] = msg_time_in_sec
                    if self.current_day_data[msg["sym"]]["init_price"] == 0:
                        # Set initial value
                        self.current_day_data[msg["sym"]]["init_price"] = msg["p"]
                    else:
                        curr_change = ((msg["p"] - self.current_day_data[msg["sym"]]["init_price"]) /
                                       self.current_day_data[msg["sym"]]["init_price"]) * 100

                        if curr_change < self.current_day_data[msg["sym"]]["min_change"]:
                            if self.current_day_data[msg["sym"]]["min_change"] != self.MIN_CHANGE_DEFAULT:
                                self.current_day_data[msg["sym"]]["min_change"] = curr_change
                                self.current_day_data[msg["sym"]]["volatility"] = self.current_day_data[msg["sym"]][
                                                                                      "max_change"] - \
                                                                                  self.current_day_data[msg["sym"]][
                                                                                      "min_change"]

                            else:
                                # Initially this code is called once per day per ticker to adjust
                                # the min, max conflict
                                self.current_day_data[msg["sym"]]["min_change"] = curr_change
                                self.current_day_data[msg["sym"]]["max_change"] = curr_change

                        elif curr_change > self.current_day_data[msg["sym"]]["max_change"]:
                            self.current_day_data[msg["sym"]]["max_change"] = curr_change
                            self.current_day_data[msg["sym"]]["volatility"] = self.current_day_data[msg["sym"]][
                                                                                  "max_change"] - \
                                                                              self.current_day_data[msg["sym"]][
                                                                                  "min_change"]
                        # Check if change is 20% or above
                        if curr_change >= 20:
                            # Check if we already sent msg today
                            if msg["sym"] not in self.today_sms_data:
                                # Check if we sent msg this week
                                if msg["sym"] not in self.current_week_sms_data:
                                    # Last 7 days first time sms requirement meet
                                    if (self.current_day_data[msg["sym"]]["volatility"] * 3) >= \
                                            self.prev_week_highest_volatility[msg["sym"]]:

                                        if self.has_news(msg["sym"]):
                                            # 3 times volatility than prev week highest volatility and has news
                                            print(
                                                "LAST_7_DAYS_FIRST_TIME_AND_3_TIMES_VOLATILITY_THAN_PREVIOUS_WEEK_HIGHEST_VOLATILITY_HAS_NEWS")
                                            print(
                                                f"SEND SMS: $ **{msg['sym']}** $ has news, prev_volatility = {self.prev_week_highest_volatility[msg['sym']]} , curr_volatility = {self.current_day_data[msg['sym']]['volatility']}")
                                            self.today_sms_data.append(msg['sym'])
                                            self.current_week_sms_data.append(msg['sym'])
                                        else:
                                            # 3 times volatility than prev week highest volatility and no news
                                            print(
                                                "LAST_7_DAYS_FIRST_TIME_AND_3_TIMES_VOLATILITY_THAN_PREVIOUS_WEEK_HIGHEST_VOLATILITY")
                                            print(
                                                f"SEND SMS: * {msg['sym']} * prev_volatility = {self.prev_week_highest_volatility[msg['sym']]} , curr_volatility = {self.current_day_data[msg['sym']]['volatility']}")
                                            self.today_sms_data.append(msg['sym'])
                                            self.current_week_sms_data.append(msg['sym'])
                                    else:

                                        if self.has_news(msg["sym"]):
                                            # Last 7 days first time and has news
                                            print("LAST_7_DAYS_FIRST_TIME_HAS_NEWS")
                                            print(f"SEND SMS: $ {msg['sym']} * $")
                                            self.today_sms_data.append(msg['sym'])
                                            self.current_week_sms_data.append(msg['sym'])
                                        else:
                                            # Last 7 days first time and no news
                                            print("LAST_7_DAYS_FIRST_TIME")
                                            print(f"SEND SMS: {msg['sym']} *")
                                            self.today_sms_data.append(msg['sym'])
                                            self.current_week_sms_data.append(msg['sym'])

                                    LAST_7_MORE_THAN_ONE_TIME = "symbol"

                                else:
                                    # More than one time in current week but today is first
                                    if self.has_news(msg["sym"]):
                                        # Last 7 days More than one time and has news
                                        print("LAST_7_MORE_THAN_ONE_TIME_HAS_NEWS")
                                        print(f"SEND SMS: $ {msg['sym']} $")
                                        self.today_sms_data.append(msg['sym'])
                                        self.current_week_sms_data.append(msg['sym'])
                                    else:
                                        # Last 7 days more than one time
                                        print("LAST_7_MORE_THAN_ONE_TIME")
                                        print(f"SEND SMS: {msg['sym']}")
                                        self.today_sms_data.append(msg['sym'])
                                        self.current_week_sms_data.append(msg['sym'])
                            else:
                                # Today we already sent a msg to the user
                                print(f"Today we already sent a message for {msg['sym']}. So skip it")


if __name__ == "__main__":
    pol = PolygonRealTimeTradeData()
