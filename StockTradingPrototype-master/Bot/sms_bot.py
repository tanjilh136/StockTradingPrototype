import time
from datetime import datetime
from threading import Thread

from Bot.sms_handler import SmsHandler
from trade_backend.trader import CustomTimeZone


class SmsBot:
    KARIMS_PHONE_NUMBER = "+14083934260"
    TWILIO_ACCOUNT_SID_PAID = 'AC94aba3c85c498faa750d6feb24b81f60'
    TWILIO_AUTH_TOKEN_PAID = 'f5b21ce9959aff8691f6cc7d11c3601c'
    TWILIO_NUMBER_PAID = "+16504354553"

    TWILIO_ACCOUNT_SID_TRIAL = 'ACb61a4deb059285cf924aa4ae147f43b6'
    TWILIO_AUTH_TOKEN_TRIAL = '0a544422bce10ac5cde63bc24e535db3'
    TWILIO_NUMBER_TRIAL = "+18043125076"

    def __init__(self, sms_receiver_phone="+14083934260"):
        self.sms_receiver_phone = sms_receiver_phone
        self.processing_received_sms = []
        # [{"from_number": "+1000000", "ticker": "aapl", "target_price": "1.3"},{"from_number": "+1000000", "ticker": "aal", "target_price": "3"}]

    def keep_processing_symbol_price_sms_command(self):
        while True:
            time.sleep(1)
            for sms_data in self.processing_received_sms:
                from_number = sms_data["from_number"]
                ticker = sms_data["ticker"]
                target_price = sms_data["target_price"]
                # Compare these data with the corresponding ticker prices
                # When  float(actual_price)<=float(target_price)  then
                self.sms_handler.send_message(to=from_number, body=f"{ticker} has reached {target_price}!",
                                              on_send_message_listener=self.user_command_sms_sent)

    def user_command_sms_sent(self, sid, to, body):
        """
        auto called when send sms requested is queued in twilio

        :param sid:
        :param to:
        :param body:
        :return:
        """
        pass

    def sms_received(self, sid="", from_number="", body=""):
        """
        This function is called when we receive a message from allowed number

        :param sid:
        :param from_number:
        :param body:
        :return:
        """
        print(sid)  # Already deleted from twilio
        print(from_number)
        print(body)
        msg = body.strip().split(" ")
        if len(msg) == 2:
            ticker = msg[0]
            target_price = msg[1]
            self.processing_received_sms.append(
                {"from_number": from_number, "ticker": ticker, "target_price": target_price})

    def start_now(self):
        """
        Starts the bot immediately

        :return:
        """
        self.sms_handler = SmsHandler(twilio_sid=bot.TWILIO_ACCOUNT_SID_TRIAL,
                                      twilio_auth_token=bot.TWILIO_AUTH_TOKEN_TRIAL,
                                      owned_phone_number=bot.TWILIO_NUMBER_TRIAL,
                                      allowed_sender_phone=bot.TWILIO_NUMBER_PAID)
        self.sms_handler.wait_for_inbound_sms(on_received_sms_listener=bot.sms_received, refresh_after=2)


    def start(self, start_time_iso="now", start_date_iso="", count_24_hr_at_iso_time="15:59:59"):
        """
        ALL OF THE TIME AND DATES MUST BE OF America/New_York Time zone
        Starts the bot at "start_time_iso" in a new thread

        :param start_time_iso: "now" or "hr:m:s" 24hr format. If "now", then start_date_iso is skipped
                               ""
        :param start_date_iso: "" or "Y-m-d" the date of the start_time_iso
        :param count_24_hr_at_iso_time: A day completes at this specific time. Considered as valid time
        :return:
        """

        self.day_end_at = count_24_hr_at_iso_time.strip()

        if start_time_iso.lower() == "now":
            t1 = Thread(target=self.start_now)
            t1.start()
        else:
            time_date = CustomTimeZone()  # Time zone is America/New_York by default
            curr_time, curr_date = time_date.get_current_iso_time_date_tuple()
            curr_year, curr_month, curr_day = curr_date.strip().split("-")
            curr_hr, curr_min, curr_sec = curr_time.strip().split(":")

            start_year, start_month, start_day = start_date_iso.strip().split("-")
            start_hr, start_min, start_sec = start_time_iso.strip().split(":")

            start_at = datetime(year=int(start_year), month=int(start_month), day=int(start_day), hour=int(start_hr),
                                minute=int(start_min), second=int(start_sec))
            curr_time_date = datetime(year=int(curr_year), month=int(curr_month), day=int(curr_day), hour=int(curr_hr),
                                      minute=int(curr_min), second=int(curr_sec))

            remaining_seconds = (start_at - curr_time_date).total_seconds()
            print(f"Bot will start at {start_date_iso}  {start_time_iso}")
            print(f"A day will be completed at {count_24_hr_at_iso_time}")
            print(f"Sleeping for {remaining_seconds} seconds")
            time.sleep(remaining_seconds)
            t1 = Thread(target=self.start_now)
            t1.start()

    def stop(self):
        """
        Stops the bot

        :return:
        """


if __name__ == "__main__":
    bot = SmsBot()
    bot.start(start_time_iso="now")
