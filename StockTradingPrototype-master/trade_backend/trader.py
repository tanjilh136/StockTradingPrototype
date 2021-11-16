import pandas as pd
import numpy as np
import alpaca_trade_api as tradeapi
from polygon import RESTClient as polygon_rest_client
from datetime import datetime
from datetime import timedelta
import sys
import websocket, json
import datetime
import pytz
import math


class CustomTimeZone:
    MACHINE_TIME_ZONE = ""
    STOCK_MARKET_LOCATION = "America/New_York"

    def __init__(self, time_zone="America/New_York"):
        """
        if time_zone == MACHINE_TIME_ZONE or "", then the current machine timezone will be considered
        :param time_zone:
        """
        self.time_zone = time_zone
        if (self.time_zone not in pytz.common_timezones) and (self.time_zone != self.MACHINE_TIME_ZONE):
            raise Exception(f"Wrong time zone : ({self.time_zone}) Valid time zones are: \n {pytz.common_timezones}")

    def get_n_min_prev_unix(self, nano_unix, n):
        """
        Reduce n minutes from given nano_unix and return the calculated nano_unix
        :param nano_unix : the base timestamp in nano second
        :param n : number of minutes that needs to be reduced from nano_unix
        :returns n minutes previous timestamp based on nano_unix param
        """
        return nano_unix - (n * 60000000000)

    def get_n_min_next_unix(self, nano_unix, n):
        """
        Add n minutes with given nano_unix and return the calculated nano_unix
        :param nano_unix : the base timestamp in nano second
        :param n : number of minutes that needs to be added with nano_unix
        :returns: n minutes next timestamp based on nano_unix param
        """
        return nano_unix + (n * 60000000000)

    def get_current_unix_time(self):
        """
        Current UTC/UNIX timestamp in nanosecond. Python datetime api returns timestamp
        in second format as float.
        :return: UNIX timestamp in nano (lossy nano second is not precise)
        """
        return int(datetime.datetime.now().timestamp() * 1000000000)

    def get_current_unix_time_in_mili(self):
        return int(datetime.datetime.now().timestamp()*1000)

    def reduce_n_day_from_iso_date(self, n, iso_date):
        """
        Subtract n day from given iso_date. It is considered that all params are valid

        :param n: total days to be subtracted
        :param iso_date: iso date from which the days will be subtracted
        :return: iso date as string
        """
        d_parts = datetime.datetime.fromisoformat(iso_date)
        reduced_date = datetime.date(d_parts.year, d_parts.month, d_parts.day) - datetime.timedelta(n)
        return str(reduced_date)

    def get_date_time_from_nano_timestamp(self, nano_unix):
        """
        Datetime is generated for specified time zone only
        :param nano_unix:
        :return:
        """

        from datetime import datetime
        from dateutil import tz
        from_zone = tz.tzutc()
        if self.time_zone != self.MACHINE_TIME_ZONE:
            to_zone = tz.gettz(self.time_zone)
        else:
            to_zone = tz.tzlocal()

        return datetime.fromtimestamp(nano_unix / 1000000000, tz=to_zone)

    def get_tz_date_from_nano_unix(self, nano_unix):
        date_time = self.get_date_time_from_nano_timestamp(nano_unix)
        return date_time.date().isoformat()

    def get_tz_time_from_nano_unix(self, nano_unix):
        date_time = self.get_date_time_from_nano_timestamp(nano_unix)
        return date_time.time().isoformat()

    def get_tz_time_date_tuple_from_nano_unix(self, nano_unix, strf="%H:%M:%S"):
        date_time = self.get_date_time_from_nano_timestamp(nano_unix)
        return date_time.time().strftime(strf), date_time.date().isoformat()

    def get_strf_tz_time_from_nano_unix(self, nano_unix, strf="%H:%M:%S"):
        date_time = self.get_date_time_from_nano_timestamp(nano_unix)
        return date_time.time().strftime(strf)

    def get_current_iso_date(self):
        """
        Calculates current date of a specific timezone
        if the timezone is "" or empty string then current machines current date is returned

        :raises Exception when given time zone is invalid:
        :returns: iso date
        """
        if self.time_zone == self.MACHINE_TIME_ZONE:
            # return current date of machine
            return datetime.datetime.now().strftime("%Y-%m-%d")
        else:
            # Time zone is valid
            utc_now = pytz.utc.localize(datetime.datetime.utcnow())

            tz_time_now = utc_now.astimezone(pytz.timezone(self.time_zone))
            print(tz_time_now)
            return tz_time_now.date().isoformat()

    def get_current_iso_time_date_tuple(self):
        """
        Calculates current date of a specific timezone
        if the timezone is "" or empty string then current machines current date is returned

        :raises Exception when given time zone is invalid:
        :returns: iso date
        """
        if self.time_zone == self.MACHINE_TIME_ZONE:
            # return current date of machine
            curr_time_date = datetime.datetime.now()

            return curr_time_date.time().strftime("%H:%M:%S"), curr_time_date.date().strftime("%Y-%m-%d")
        else:
            # Time zone is valid
            utc_now = pytz.utc.localize(datetime.datetime.utcnow())

            tz_time_now = utc_now.astimezone(pytz.timezone(self.time_zone))
            print(tz_time_now)
            return tz_time_now.time().strftime("%H:%M:%S"), tz_time_now.date().strftime("%Y-%m-%d")


class PolygonData:
    def __init__(self):
        self.auth_key = "Zay2cQZwZfUTozLiLmyprY4Sr3uK27Vp"
        self.time_ob = CustomTimeZone()
        self.current_date = self.time_ob.get_current_iso_date()

    def get_prev_n_days_trade_data(self, symbol, total_prev_day=0, timespane="minute"):
        """
        Fetch history of stock data from current date to prev n day
        :param symbol: Ticker name
        :param total_prev_day: n days to get history of trade from current date
        :param timespane: datainterval in minute,hour,day etc
        :return: pd.DataFrame() of trade history
        """
        high = []
        low = []
        open = []
        close = []
        time = []
        volume = []
        df = pd.DataFrame()
        c_time = CustomTimeZone()
        highest_date = c_time.get_current_iso_date()
        lowest_date = c_time.reduce_n_day_from_iso_date(total_prev_day, highest_date)
        with polygon_rest_client(self.auth_key) as client:
            resp = client.stocks_equities_aggregates(symbol, 1, timespane, lowest_date, highest_date, limit=50000)
            for i in range(0, len(resp.results)):
                high.append(resp.results[i]["h"])
                low.append(resp.results[i]["l"])
                open.append(resp.results[i]["o"])
                close.append(resp.results[i]["c"])
                # here 't' is in milisec, but customtimezone requires nano_sec
                nano_time = int(int(resp.results[i]["t"]) * 1000000)
                share_date_time = str(c_time.get_date_time_from_nano_timestamp(nano_time))
                time.append(share_date_time)
                volume.append(resp.results[i]["v"])

            df["time"] = time
            df["high"] = high
            df["low"] = low
            df["open"] = open
            df["close"] = close
            df["volume"] = volume
            return df

    def get_30_min_res_with_quantity_formula(self, df):
        """
        1. Separates 30 mins of data into three separate 10 mins dataframe
        2. Calculate average of three different dataframes
        3. Apply quantity formula

        :param df: dataframe returned from get_last_30_min_data function.
                   Format: pd.DataFrame()["time","column"] or None
        :return: int -  by flooring the calculated value
        """
        if (df is None) or len(df) < 3:
            return 0
        else:
            first_10_min = df.loc[df["time"] <= (self.time_ob.get_n_min_next_unix(df["time"][0], 10))]
            second_10_min = df.loc[(df["time"] > self.time_ob.get_n_min_next_unix(df["time"][0], 10)) & (
                    df["time"] <= self.time_ob.get_n_min_next_unix(df["time"][0], 20))]
            third_10_min = df.loc[df["time"] > (self.time_ob.get_n_min_next_unix(df["time"][0], 20))]

            A = sum(first_10_min['price']) / len(first_10_min['price'])
            B = sum(second_10_min['price']) / len(second_10_min['price'])
            C = sum(third_10_min['price']) / len(third_10_min['price'])
            return math.floor(((A * 3) + (B * 2) + C) / 120)

    def get_time_n_sales(self, symbol):

        time = []
        price = []
        volume = []
        time.append("Time")
        price.append("Price")
        volume.append("Volume")

        current_date = self.time_ob.get_current_iso_date()

        with polygon_rest_client(self.auth_key) as client:
            print("Please wait")
            time_n_sales = client.historic_trades_v2(symbol, current_date)
            print("Time and sales data fetched")

        print("..............")
        print(time_n_sales.results)
        print(len(time_n_sales.results))

        for i in time_n_sales.results:
            price.append(str(i['p']))
            t = self.time_ob.get_tz_time_from_nano_unix(int(i["y"]))
            time.append(str(t))
            volume.append(str(i['s']))

        df_ = pd.DataFrame()

        df_['Time'] = time
        df_['price'] = price
        df_['volume'] = volume
        df_.to_csv("time_and_sales.csv", index=False)
        return df_

    def get_recent_data(self, symbol, target_iso_date="2021-05-14"):
        """
        Collect last 30 minutes of trade data from polygon.io using restapi.
        Current time is considered as nano_unix timestamp.
        This function uses custom paging mechanism to get data from polygon
        if data is not available then returns None

        :param symbol: ticker symbol which data need to be scraped
        :param target_iso_date: Iso format of a date only which will be checked for data scraping
        :return: pd.DataFrame()["time","column"] or None
        """
        df = pd.DataFrame()
        current_stamp = self.time_ob.get_current_unix_time()
        recent_stamp = self.time_ob.get_n_min_prev_unix(current_stamp, 30)
        with polygon_rest_client(self.auth_key) as client:
            prices = []
            time_unixs = []
            collecting = True
            while collecting:
                resp = client.historic_trades_v2(symbol, target_iso_date, timestamp=recent_stamp,
                                                 timestampLimit=current_stamp)
                for i in resp.results:
                    prices.append(i['p'])
                    time_unixs.append(i['y'])

                try:
                    if recent_stamp == time_unixs[(len(time_unixs) - 1)]:
                        collecting = False
                    else:
                        recent_stamp = time_unixs[(len(time_unixs) - 1)]
                except IndexError:
                    print("Last 30 min data is not available")
                    return None

            df["price"] = prices
            df["time"] = time_unixs
            return df

    def get_last_30_min_data(self, symbol):
        """
        Collect last 30 minutes of trade data from polygon.io using restapi.
        Current time is considered as nano_unix timestamp.
        This function uses custom paging mechanism to get data from polygon
        if data is not available then returns None

        :param symbol: ticker symbol which data need to be scraped
        :param target_iso_date: Iso format of a date only which will be checked for data scraping
        :return: pd.DataFrame()["time","column"] or None
        """
        df = pd.DataFrame()
        current_stamp = self.time_ob.get_current_unix_time()
        recent_stamp = self.time_ob.get_n_min_prev_unix(current_stamp, 30)
        target_iso_date = self.time_ob.get_current_iso_date()
        with polygon_rest_client(self.auth_key) as client:
            prices = []
            time_unixs = []
            collecting = True
            while collecting:
                resp = client.historic_trades_v2(symbol, target_iso_date, timestamp=recent_stamp,
                                                 timestampLimit=current_stamp)
                for i in resp.results:
                    prices.append(i['p'])
                    time_unixs.append(i['y'])

                try:
                    if recent_stamp == time_unixs[(len(time_unixs) - 1)]:
                        collecting = False
                    else:
                        recent_stamp = time_unixs[(len(time_unixs) - 1)]
                except IndexError:
                    print("Last 30 min data is not available")
                    return None

            df["price"] = prices
            df["time"] = time_unixs
            return df


class AlpakaTrader:
    SHORTABLE = "S"
    NON_SHORTABLE = "N"
    COMPANY_FETCH_ERROR = "NOT FOUND"
    SHORTABLE_FETCH_ERROR = "NOT FOUND"

    def __init__(self):
        self.authorized_alpaka_api = self.authorize_alpaka_api()
        self.alpaka_account_info = self.get_alpaka_account()
        self.symbol_asset = None

    def authorize_alpaka_api(self):
        """
        creates an authorized alpaka.market api with (API_KEY, SECRET_KEY, BASE_URL)

        :return: alpaka.market authenticated api
        """

        API_KEY = 'PK5616ETLC9V7KJ9J4Q5'
        SECRET_KEY = 'Uz8UtHjPRw6x71whpJgHgYPRHqxAjlcmML2MPmRb'
        BASE_URL = 'https://paper-api.alpaca.markets'  # Change this url when live trading
        return tradeapi.REST(
            API_KEY,
            SECRET_KEY,
            BASE_URL
        )

    def fetch_client_info_data(self):
        list_order = self.authorized_alpaka_api.list_orders(status=all)
        df = pd.DataFrame()
        ticker = []
        action = []
        share = []
        fill_price = []
        live_price = []
        status = []
        pending = []
        click_to_close = []
        click_to_close_market = []

        # Adding columns manually
        ticker.append("Ticker")
        action.append("Action")
        share.append("Share")
        fill_price.append("Fill Price")
        live_price.append("Live Price")
        status.append("Status")
        pending.append("Pending")
        click_to_close.append("Click to close")
        click_to_close_market.append("Click to close market")

        print("Fetching pending order table")
        for i in range(0, len(list_order)):
            ticker.append(list_order[i].symbol)
            action.append(list_order[i].side)
            share.append(str(list_order[i].qty))
            fill_price.append(str(list_order[i].filled_avg_price))
            live_price.append(str(self.authorized_alpaka_api.get_last_trade(list_order[i].symbol).price))
            status.append(list_order[i].status)
            pending.append("pending")
            click_to_close.append("close")
            click_to_close_market.append("close market")

        # Another column are added. Two sets of column is added, just for the help
        df["Ticker"] = ticker
        df["Action"] = action
        df["Share"] = share
        df["Fill Price"] = fill_price
        df["Live Price"] = live_price
        df["Status"] = status
        df["Pending"] = pending
        df["Click to close"] = click_to_close
        df["Click to close market"] = click_to_close_market
        print("Pending order table fetched")
        return df

    def get_alpaka_account(self):
        """
        considering that self.authorized_alpaka_api object is created and valid

        :return: account info of alpaka authenticated api
        """
        return self.authorized_alpaka_api.get_account()

    def fetch_and_set_symbol_asset(self, symbol):
        """
        Fetch asset from alpaka api and set the asset in "self.symbol_asset"

        :param symbol: name of the symbol which asset will be fetched from "self.authorized_alpaka_api" object
        :return: bool
        """
        try:
            self.symbol_asset = self.authorized_alpaka_api.get_asset(symbol)
            return True
        except Exception:
            return False

    def get_current_symbol_shortable_status(self):
        """
        shortable status of the current symbol
        self.symbol_asset contains info of the current symbol.
        :return: str - SHORTABLE/NON_SHORTABLE
        """
        if self.symbol_asset.shortable:
            return self.SHORTABLE
        else:
            return self.NON_SHORTABLE

    def get_company_name(self):
        """
        company name of the current symbol.
        self.symbol_asset contains info of the current symbol.

        :return: str - company name of the current symbol
        """
        return self.symbol_asset.name

    def get_symbol_name(self):
        """
        returns the symbol name from symbol_asset which was set earlier by calling "self.fetch_and_set_symbol_asset".

        :return: symbol
        """
        return self.symbol_asset.symbol

    def buy_order(self, order_type, symbol, quantity, **kwargs):
        """
        Buy some given quantity of given symbol based on given order_type
        Currently supports three order_types - limit, market, stop_limit.

        :param order_type: str - allowed types are limit, stop limit, market.
        :param symbol: str - ticker symbol that you want to buy.
        :param quantity: str - integer quantity as string. The quantity you want to buy.
        :param kwargs: used for other important parameter. For example limit_price when the order type is limit,
                    limit_price and stop_price when the order is stop_limit.
        :return: Order Object
        """
        if order_type == 'market':
            return self.authorized_alpaka_api.submit_order(
                symbol=symbol,
                qty=quantity,
                side='buy',
                type=order_type,
                time_in_force='gtc'
            )
        elif order_type == 'limit':
            limit_price = float(kwargs["limit_price"])
            return self.authorized_alpaka_api.submit_order(
                symbol=symbol,
                qty=quantity,
                side='buy',
                type=order_type,
                time_in_force='opg',
                limit_price=limit_price
            )
        elif order_type == "stop_limit":
            limit_price = float(kwargs["limit_price"])
            stop_price = float(kwargs["stop_price"])
            return self.authorized_alpaka_api.submit_order(
                symbol=symbol,
                qty=quantity,
                side='buy',
                type=order_type,
                time_in_force='opg',
                limit_price=limit_price,
                stop_price=stop_price
            )

    def sell_order(self, order_type, symbol, quantity, **kwargs):
        """
        Sell some given quantity of given symbol based on given order_type
        Currently supports three order_type - limit, market, stop_limit

        :param order_type: str - allowed types are limit, stop_limit, market
        :param symbol: str - ticker symbol that you want to sell
        :param quantity: str - integer quantity as string. The quantity you want to sell
        :param kwargs: used for other important parameter. For example limiting_price when the order type is limit,
                       limit_price and stop_price when the order is stop_limit
        :return: Order_Object
        """

        if order_type == 'market':
            return self.authorized_alpaka_api.submit_order(
                symbol=symbol,
                qty=quantity,
                side='sell',
                type=order_type,
                time_in_force='gtc'
            )
        elif order_type == 'limit':
            limit_price = float(kwargs["limit_price"])
            return self.authorized_alpaka_api.submit_order(
                symbol=symbol,
                qty=quantity,
                side='sell',
                type=order_type,
                time_in_force='opg',
                limit_price=limit_price
            )
        elif order_type == "stop_limit":
            limit_price = float(kwargs["limit_price"])
            stop_price = float(kwargs["stop_price"])
            return self.authorized_alpaka_api.submit_order(
                symbol=symbol,
                qty=quantity,
                side='sell',
                type=order_type,
                time_in_force='opg',
                limit_price=limit_price,
                stop_price=stop_price
            )

    def double_buy_sell_checker(self, symbol):
        order_list_all = self.authorized_alpaka_api.list_orders(status=all)
        for i in range(0, len(order_list_all)):
            if order_list_all[i].status == ('partially_filled' and 'filled'):
                if (order_list_all[i].symbol == symbol) and (order_list_all[i].side == 'sell'):
                    return True, order_list_all

        return False

    def double_buy(self, order_list_all, order_type, symbol, **kwargs):
        print(order_type, symbol, kwargs)
        amount_of_stock = 0
        # measuring amount of stock here
        for i in range(0, len(order_list_all)):
            if (order_list_all[i].status == 'filled') and (order_list_all[i].side == 'sell') and (
                    order_list_all[i].symbol == symbol):
                amount_of_stock = amount_of_stock + int(order_list_all[i].qty)
        print("Clicking Buy order")
        self.buy_order(order_type, symbol, (amount_of_stock * 2), **kwargs)
        print("Bought")

    def double_sell(self, order_list_all, order_type, symbol, **kwargs):
        sold_stock = 0
        bought_stock = 0
        # measuring amount of stock here
        for i in range(0, len(order_list_all)):
            if (order_list_all[i].status == 'filled') and (order_list_all[i].side == 'sell') and (
                    order_list_all[i].symbol == symbol):
                sold_stock = sold_stock + int(order_list_all[i].qty)
            if (order_list_all[i].status == 'filled') and (order_list_all[i].side == 'buy') and (
                    order_list_all[i].symbol == symbol):
                bought_stock = bought_stock + int(order_list_all[i].qty)

        self.sell_order(order_type, symbol, (bought_stock - sold_stock), **kwargs)

    def get_symbol_order_history(self, status="FILL"):
        res = self.authorized_alpaka_api.get_activities(status)
        print(res)


if __name__ == "__main__":
    pol = PolygonData()
    # print(pol.get_30_min_res_with_quantity_formula(pol.get_last_30_min_data("AAPL")))
    # pol.time_n_sales("AAPL")
    # df = pol.get_time_sales_data("AAPL")
    # print(df)
