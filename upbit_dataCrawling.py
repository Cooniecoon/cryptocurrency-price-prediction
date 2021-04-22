import pandas as pd
import numpy as np
import pyupbit
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

def day_crawller(code, date):
    req = requests.get(
        f"https://crix-api-endpoint.upbit.com/v1/crix/candles/days/?code=CRIX.UPBIT.KRW-{code}&count=1000&to={date}"
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
    
    return coin_data

def get_days_data(code, save=False,save_root='./'):
    time = datetime.now()
    date=str(time).split(' ')[0]+' 00:00:00'
    print(date)
    data = day_crawller(code, date)

    while True:
        time=time - timedelta(hours=400)
        date=str(time).split(' ')[0]+' 00:00:00'
        print(date)
        
        data=pd.concat([data,day_crawller(code, date)])

        if time < datetime(2017, 10, 31, 0, 0, 0):
            break
    data = data.sort_values(by=["Time"], axis=0)
    if save is True:
        data.to_csv(save_root+"Upbit_BTC_daysData.csv",index=False)
    return data

def minutes_crawller(code, minute, date):
    req = requests.get(
        f"https://crix-api-endpoint.upbit.com/v1/crix/candles/minutes/{minute}?code=CRIX.UPBIT.KRW-{code}&count=1000&to={date}"
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
    
    return coin_data

def get_minutes_data(code, minute, save=False, save_root='./'):
    time = datetime.now()
    date=str(time).split(' ')[0]+' 00:00:00'
    print(date)
    data = minutes_crawller(code, minute, date)

    while True:
        time=time - timedelta(hours=400*int(minute)//60)
        date=str(time).split(' ')[0]+' 00:00:00'
        print(date)
        
        data=pd.concat([data,minutes_crawller(code, minute, date)])

        if time < datetime(2017, 10, 31, 0, 0, 0):
            break
    data = data.sort_values(by=["Time"], axis=0)
    if save is True:
        data.to_csv(save_root+f"Upbit_BTC_{minute}_Data.csv",index=False)
    return data

COIN_LIST=['BTC','BCH','BTG','BSV','BCHA','LTC','EMC2','ETH','ETC','ZIL','ADA']

Data_save_Path="./data/"

code = "BTC"

get_days_data(code,save=True,save_root=Data_save_Path)
get_minutes_data(code, minute='240', save=True, save_root=Data_save_Path)