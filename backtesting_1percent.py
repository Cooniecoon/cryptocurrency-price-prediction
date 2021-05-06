import pyupbit
import plotly.graph_objects as go 
from plotly.subplots import make_subplots
import time
import pandas as pd

def SMA(data, period=15, column='close'):
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

def percent_R(df, period = 14, column = 'close'):
    df['H14']=df['high'].rolling(window=period).max().shift(1)
    df['L14']=df['low'].rolling(window=period).min().shift(1)
    df['per_R']=(df['H14']-df['close'])/(df['H14']-df['L14'])*(-100)
    return df

def get_ohlcv(ticker,rep):
    dfs = [ ]
    # df = pyupbit.get_ohlcv(ticker, interval="minute1", to="20210423 11:00:00")
    df = pyupbit.get_ohlcv(ticker, interval="minute1")
    dfs.append(df)

    for i in range(rep):
        df = pyupbit.get_ohlcv(ticker, interval="minute1", to=df.index[0])
        dfs.append(df)
        time.sleep(0.1)
        # print(i)

    df = pd.concat(dfs)
    df = df.sort_index()
    return df

def short_trading_for_1percent(df,RSI,per_R):    
    sell_ror=0.011
    buy_ror=1.01
    ma_threshold=1.01
    # ma_threshold=1.03
    ma15 = df['close'].rolling(15).mean().shift(1)
    ma50 = df['close'].rolling(50).mean().shift(1)
    ma120 = df['close'].rolling(90).mean().shift(1)

    # 1) 매수 일자 판별
    cond_0 = df['high'] >= df['open'] * buy_ror
    cond_1 = (ma15 >= ma50) & (ma15 <= ma50 * ma_threshold)
    cond_2 = ma50 > ma120

    cond_3 = df['RSI']<RSI 
    cond_4 = df['per_R']<per_R
    
    cond_5 = df['RSI']<50
    cond_6 = df['per_R']<-95

    cond_buy = cond_0 & cond_1 & cond_2 &  cond_4 #| cond_5&cond_6&cond_0 #& df['RSI']>10
    # print('매수기회 : ',len(df.index[cond_buy]))
    acc_ror = 1
    sell_date = None
    sell_count=0
    ax_ror = []
    ay_ror = []

    # 2) 매도 조건 탐색 및 수익률 계산
    for buy_date in df.index[cond_buy]:
        if sell_date != None and buy_date <= sell_date:
            continue

        target = df.loc[ buy_date :  ]

        cond = target['high'] >= df.loc[buy_date, 'open'] * (sell_ror+buy_ror)
        sell_candidate = target.index[cond]
        
        if len(sell_candidate) == 0:
            buy_price = df.loc[buy_date, 'open'] * (sell_ror+buy_ror)
            sell_price = df.iloc[-1, 3]
            acc_ror *= (sell_price / buy_price)
            ax_ror.append(df.index[-1])
            ay_ror.append(acc_ror)
            sell_count+=1
            # print('!acc_ror',acc_ror)
            break
        else:
            sell_date = sell_candidate[0]
            acc_ror *= (1+sell_ror-0.001-0.004)
            ax_ror.append(sell_date)
            ay_ror.append(acc_ror)
            # print('acc_ror',acc_ror)
            sell_count+=1
            # 수수료 0.001 + 슬리피지 0.004
    # print('매도 회수 : ',sell_count)
    
    # candle = go.Candlestick(
    #     x = df.index,
    #     open = df['open'],
    #     high = df['high'],
    #     low = df['low'],
    #     close = df['close'],
    # )

    # ror_chart = go.Scatter(
    #     x = ax_ror,
    #     y = ay_ror
    # )

    # fig = make_subplots(specs=[ [{ "secondary_y": True }] ])
    # fig.add_trace(candle)
    # fig.add_trace(ror_chart, secondary_y=True)

    # for idx in df.index[cond_buy]:
    #     fig.add_annotation(
    #         x = idx,
    #         y = df.loc[idx, 'open']
    #     )
    # fig.show()

    return acc_ror
COIN_LIST=['BTC','BCH','BTG','BSV','BCHA','LTC','EOS','ETH','ETC','ZIL','ADA','XRP','DOT','XLM','ATOM']
# COIN_LIST=['DOT']
# COIN_LIST=['DOGE']
# COIN_LIST=['BTG','LTC']

# for ticker in COIN_LIST:
#     ticker='KRW-'+ticker
#     df = get_ohlcv(ticker,200)
#     df.to_csv(f"./data/price/{ticker}_1min.csv")

for ticker in COIN_LIST:
    ticker='KRW-'+ticker
    df = pd.read_csv(f"./data/price/{ticker}_1min.csv", index_col=0)
    df = RSI(df)
    df = percent_R(df)
    # df =df.iloc[30000:]
    rsi=40
    per_R=-30
    ror = short_trading_for_1percent(df,rsi,per_R)
    기간수익률 = df.iloc[-1, 3] / df.iloc[0, 0]
    print(ticker.ljust(8), f"ror : {ror:.2f}", f"기간수익률 : {기간수익률:.2f}")
print('RSI :',rsi,'%R :',per_R)
print(df.index[0],'부터 ',df.index[-1],'까지')