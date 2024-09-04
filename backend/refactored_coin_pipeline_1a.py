from config import *
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from utils.refactor_data_updater import *
from utils.refactor_api_getter import *

load_dotenv(override=True)
gc_api_key = os.getenv('GECKO_API') 
DB_USERNAME = os.getenv('RDS_USERNAME') 
DB_PASSWORD = os.getenv('RDS_PASSWORD') 
DB_HOST = os.getenv('RDS_ENDPOINT') 
DB_NAME = 'financial_data'

'''
Coin Price Refresh Pipeline
Cadence: AUTOMATIC DAILY
  1. Download HOURLY hist price json from coin gecko
  2. Insert HOURLY OHLC data into DB
'''

# download last 5 days data - partial update for faster runtime
end_date = datetime.now() 
start_date = end_date - timedelta(days=5)
api_getter = coin_gecko_hourly_ohlc_api_getter(api_key=gc_api_key, 
                                   data_save_path=GECKO_HOURLY_JSON_PATH,
                                   start_date=start_date,
                                   end_date=end_date)
api_getter.download_data()

# insert to DB
# OHLC
db = coin_gecko_OHLC_hourly_db_refresher(DB_NAME, DB_HOST, DB_USERNAME, DB_PASSWORD, "coin_historical_price")
db.connect()
db.create_table()
for filename in os.listdir(GECKO_DAILY_JSON_PATH):
    if filename.endswith('.json'):
        file_path = os.path.join(GECKO_DAILY_JSON_PATH, filename)
        db.insert_data(file_path)
db.close()
