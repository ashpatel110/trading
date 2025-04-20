# nifty data: https://www.nseindia.com/report-detail/fo_eq_security
import json
from datetime import datetime

import requests
from cachetools import TTLCache, cached

from common import common

DATA_FOLDER = "C:/Users/ashpa/algo trading/trading/data/short_straddle/data"
NIFTY_50_CSV_FILENAME = "nifty_50.csv"
MONTHLY_EXPIRY_FILENAME = "monthly_expiry.json"

cache = TTLCache(maxsize=1, ttl=900)


def get_nifty_50_data():
    with open(f"{DATA_FOLDER}/{NIFTY_50_CSV_FILENAME}") as csv_file:
        csv_data = csv_file.read()
        rows = csv_data.split("\n")[1:]
        return {
            datetime.strptime(str_date, "%d-%b-%Y"):
                common.OHLC(
                    open=float(str_open),
                    high=float(str_high),
                    low=float(str_low),
                    close=float(str_close),
                )
            for str_date, str_open, str_high, str_low, str_close, _, _ in map(lambda row: row.split(","), rows)
        }


def get_expiry_data():
    with open(f"{DATA_FOLDER}/{MONTHLY_EXPIRY_FILENAME}") as json_file:
        return [datetime.strptime(str_date, "%d-%b-%Y") for str_date in json.loads(json_file.read())]


@cached(cache)
def get_nse_site_request_session():
    headers = {
        'accept': '*/*',
        'accept-language': 'en-GB,en;q=0.9',
        'priority': 'u=1, i',
        'referer': 'https://www.nseindia.com/report-detail/fo_eq_security',
        'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
    }

    session = requests.Session()
    session.headers.update(headers)

    # set cookies
    session.get("https://www.nseindia.com/report-detail/fo_eq_security")
    return session


def get_instrument_data(from_date, to_date, instrument_type, symbol, year, expiry_date, option_type, strike_price):
    session = get_nse_site_request_session()
    url_params = {
        "from": from_date.strftime("%d-%m-%Y"),
        "to": to_date.strftime("%d-%m-%Y"),
        "instrumentType": instrument_type,
        "symbol": symbol,
        "year": str(year),
        "expiryDate": expiry_date.strftime("%d-%b-%Y"),
        "optionType": option_type,
        "strikePrice": str(strike_price),
    }
    url = f"https://www.nseindia.com/api/historical/foCPV?{"&".join([f"{key}={value}" for key, value in url_params.items()])}"

    response = session.get(url, headers=session.headers)
    if response.status_code == 200:
        json_response = response.json()
        if "data" in json_response and json_response.get("data"):
            return json_response.get("data")[0]
    print(response)
    return None


def get_nifty_50_options_data(from_date, to_date, year, expiry_date, option_type, strike_price):
    return get_instrument_data(from_date, to_date, "OPTIDX", "NIFTY", year, expiry_date, option_type, strike_price)

# print(get_nifty_50_data())
# print(get_expiry_data())
# print(get_nifty_50_options_data(
#     datetime(2025, 1, 1),
#     datetime(2025, 1, 1), 2025, datetime(2025, 1, 30), "CE", 22000)
# )
