import requests
import datetime
import pandas as pd
from time import sleep


def datetime2str(datetime):
    datetime = str(datetime).split(" ")
    yyyymmdd = datetime[0]
    hhmmss = datetime[1][:8]

    url_form = yyyymmdd + "T" + hhmmss + "+09:00"
    return url_form


def candle_crawller(time_step, time, code):
    if time_step in [1, 3, 5, 10, 15, 30, 60, 240]:
        url = "https://api.upbit.com/v1/candles/minutes/" + str(time_step)
        coin_code = "KRW-" + code
        querystring = {"market": coin_code, "to": str(time), "count": "200"}

        response = requests.request("GET", url, params=querystring)
        # print(time)
        result = []
        data = response.json()
        data.reverse()
        # print(len(data))
        if len(data) > 0:
            for i, candle in enumerate(data):

                result.append(
                    {
                        "Time": data[i]["candle_date_time_kst"],
                        "OpeningPrice": data[i]["opening_price"],
                        "HighPrice": data[i]["high_price"],
                        "LowPrice": data[i]["low_price"],
                        "TradePrice": data[i]["trade_price"],
                        "CandleAccTradeVolume": data[i]["candle_acc_trade_price"],
                        "candleAccTradePrice": data[i]["candle_acc_trade_volume"],
                    }
                )

    elif time_step in ["days", "weeks", "months"]:
        url = "https://api.upbit.com/v1/candles/" + str(time_step)
        coin_code = "KRW-" + code
        querystring = {"market": coin_code, "to": str(time), "count": "200"}

        response = requests.request("GET", url, params=querystring)
        # print(time)
        result = []
        data = response.json()
        data.reverse()
        # print(len(data))
        if len(data) > 0:
            for i, candle in enumerate(data):

                result.append(
                    {
                        "Time": data[i]["candle_date_time_kst"],
                        "OpeningPrice": data[i]["opening_price"],
                        "HighPrice": data[i]["high_price"],
                        "LowPrice": data[i]["low_price"],
                        "TradePrice": data[i]["trade_price"],
                        "CandleAccTradeVolume": data[i]["candle_acc_trade_price"],
                        "candleAccTradePrice": data[i]["candle_acc_trade_volume"],
                    }
                )

    coin_data = pd.DataFrame(result)
    return coin_data


code = "BTC"
time_step = 10  # 1,3,5,10,15,30,60,240, days
start_date = datetime.datetime(2017, 9, 26, 12, 00, 00)


start_date_str = datetime2str(start_date)
now = datetime.datetime.now()


if time_step in [1, 3, 5, 15, 10, 30, 60, 240]:
    next_time = start_date + datetime.timedelta(minutes=time_step * 200)
    data = candle_crawller(time_step, start_date_str, code)

    while now + datetime.timedelta(minutes=time_step * 200) > next_time:
        data = pd.concat(
            [data, candle_crawller(time_step, datetime2str(next_time), "BTC")]
        )
        next_time = next_time + datetime.timedelta(minutes=time_step * 200)
        print(next_time)
        sleep(0.05)

elif time_step in ["days", "weeks", "months"]:
    next_time = start_date + datetime.timedelta(days=1 * 200)
    data = candle_crawller(time_step, start_date_str, code)

    while now + datetime.timedelta(days=1 * 200) > next_time:
        data = pd.concat(
            [data, candle_crawller(time_step, datetime2str(next_time), "BTC")]
        )
        next_time = next_time + datetime.timedelta(days=1 * 200)
        print(next_time)
        sleep(0.05)

data.to_csv(f"data/{code}_KRW_{str(time_step)}.csv")
# # print(coin_data.info())