import pyupbit
import plotly.graph_objects as go 
from plotly.subplots import make_subplots
import time
import pandas as pd
import numpy as np

def SMA(data, period=30, column='close'):
    return data[column].rolling(window=period).mean()


def RSI(data, period = 14, column = 'close'):
    delta = data[column].diff(1) #Use diff() function to find the discrete difference over the column axis with period value equal to 1
    delta = delta.dropna() # or delta[1:]
    up =  delta.copy() #Make a copy of this object’s indices and data
    down = delta.copy() #Make a copy of this object’s indices and data
    up[up < 0] = 0 
    down[down > 0] = 0 
    data['up'] = up
    data['down'] = down
    AVG_Gain = SMA(data, period, column='up')#up.rolling(window=period).mean()
    AVG_Loss = abs(SMA(data, period, column='down'))#abs(down.rolling(window=period).mean())
    RS = AVG_Gain / AVG_Loss
    RSI = 100.0 - (100.0/ (1.0 + RS))

    data['RSI'] = RSI
    return data

def get_ohlcv(ticker):
    dfs = [ ]
    # df = pyupbit.get_ohlcv(ticker, interval="minute1", to="20210423 11:00:00")
    df = pyupbit.get_ohlcv(ticker, interval="minute1",to="20210430 11:00:00")
    dfs.append(df)

    for i in range(2):
        df = pyupbit.get_ohlcv(ticker, interval="minute1", to=df.index[0])
        dfs.append(df)
        time.sleep(0.1)
        # print(i)

    df = pd.concat(dfs)
    df = df.sort_index()
    return df

# COIN_LIST=['BTC','BCH','BTG','BSV','BCHA','LTC','EOS','ETH','ETC','ZIL','ADA','XRP','DOT','XLM','ATOM']
# COIN_LIST=['DOT']
COIN_LIST=['BTG','LTC']
# COIN_LIST=['DOGE']
# for ticker in COIN_LIST:
#     ticker='KRW-'+ticker
#     df = get_ohlcv(ticker)
#     df.to_csv(f"./data/price/{ticker}_1min.csv")
COIN_LIST=['BTG']
for ticker in COIN_LIST:
    ticker='KRW-'+ticker
    df = pd.read_csv(f"./data/price/{ticker}_1min.csv", index_col=0)
    df=RSI(df)
print(df.head(40))
print(df.index[0],'부터 ',df.index[-1],'까지')