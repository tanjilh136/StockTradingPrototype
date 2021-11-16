from datetime import datetime, timedelta
from trade_backend.trader import CustomTimeZone
custom_time = CustomTimeZone()
curr_year, curr_month, curr_day = custom_time.get_current_iso_date().strip().split("-")

print(today_date + timedelta(days=1))

