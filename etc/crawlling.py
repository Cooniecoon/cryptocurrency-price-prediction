import requests
import pandas as pd
from bs4 import BeautifulSoup
import datetime

coin_list = ["DOT"]  # "BTC", "ETH", "QKC", "SSX"

time_units = ["days", "weeks"]
minutes_units = [1, 3, 5, 15, 30, 60, 240]
count = 400  # max : 400
now = datetime.datetime.now()
yyyy = now.year
mm = now.month
dd = now.day
tttt = str(now.hour) + "_" + str(now.minute) + "_" + str(now.second)

for coin in coin_list:

    for time_unit in time_units:
        req = requests.get(
            f"https://crix-api-endpoint.upbit.com/v1/crix/candles/{time_unit}?code=CRIX.UPBIT.KRW-{coin}&count={count}"
        )
        data = req.json()
        result = []

        for i, candle in enumerate(data):
            result.append(
                {
                    "Time": data[i]["candleDateTimeKst"],
                    "OpeningPrice": data[i]["openingPrice"],
                    "HighPrice": data[i]["highPrice"],
                    "LowPrice": data[i]["lowPrice"],
                    "TradePrice": data[i]["tradePrice"],
                    "CandleAccTradeVolume": data[i]["candleAccTradeVolume"],
                    "candleAccTradePrice": data[i]["candleAccTradePrice"],
                }
            )

        coin_data = pd.DataFrame(result)
        coin_data.to_csv(f"data/{coin}_KRW_{time_unit}_{yyyy}_{mm}_{dd}.csv")

    for minute_unit in minutes_units:
        req = requests.get(
            f"https://crix-api-endpoint.upbit.com/v1/crix/candles/minutes/{minute_unit}?code=CRIX.UPBIT.KRW-{coin}&count={count}"
        )
        data = req.json()
        result = []

        for i, candle in enumerate(data):
            result.append(
                {
                    "Time": data[i]["candleDateTimeKst"],
                    "OpeningPrice": data[i]["openingPrice"],
                    "HighPrice": data[i]["highPrice"],
                    "LowPrice": data[i]["lowPrice"],
                    "TradePrice": data[i]["tradePrice"],
                    "CandleAccTradeVolume": data[i]["candleAccTradeVolume"],
                    "candleAccTradePrice": data[i]["candleAccTradePrice"],
                }
            )

        coin_data = pd.DataFrame(result)
        coin_data.to_csv(f"data/{coin}_KRW_{minute_unit}_{yyyy}_{mm}_{dd}_{tttt}.csv")
