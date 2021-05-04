import pyupbit
import plotly.graph_objects as go 
from plotly.subplots import make_subplots
import time
import pandas as pd

def get_ohlcv(ticker):
    dfs = [ ]
    # df = pyupbit.get_ohlcv(ticker, interval="minute1", to="20210423 11:00:00")
    df = pyupbit.get_ohlcv(ticker, interval="minute1")
    dfs.append(df)

    for i in range(1000):
        df = pyupbit.get_ohlcv(ticker, interval="minute1", to=df.index[0])
        dfs.append(df)
        time.sleep(0.1)

    df = pd.concat(dfs)
    df = df.sort_index()
    return df

def short_trading_for_1percent(df):    
    sell_ror=0.011
    buy_ror=1.01
    ma_threshold=1.0233
    ma15 = df['close'].rolling(15).mean().shift(1)
    ma50 = df['close'].rolling(50).mean().shift(1)
    ma120 = df['close'].rolling(90).mean().shift(1)

    # 1) 매수 일자 판별
    cond_0 = df['high'] >= df['open'] * buy_ror
    cond_1 = (ma15 >= ma50) & (ma15 <= ma50 * ma_threshold)
    cond_2 = ma50 > ma120
    cond_buy = cond_0 & cond_1 & cond_2

    acc_ror = 1
    sell_date = None

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
            break
        else:
            sell_date = sell_candidate[0]
            acc_ror *= (1+sell_ror-0.001-0.004)
            ax_ror.append(sell_date)
            ay_ror.append(acc_ror)
            # 수수료 0.001 + 슬리피지 0.004

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
# COIN_LIST=['BTC','BCH','BTG','BSV','BCHA','LTC','EOS','ETH','ETC','ZIL','ADA','XRP','DOT','XLM','ATOM']
# COIN_LIST=['DOT']
COIN_LIST=['BTG']
# for ticker in COIN_LIST:
#     ticker='KRW-'+ticker
#     df = get_ohlcv(ticker)
#     df.to_csv(f"./data/price/{ticker}_3min_test.csv")

for ticker in COIN_LIST:
    ticker='KRW-'+ticker
    df = pd.read_csv(f"./data/price/{ticker}_1min.csv", index_col=0)
    # df =df.iloc[:2000]
    ror = short_trading_for_1percent(df)
    기간수익률 = df.iloc[-1, 3] / df.iloc[0, 0]
    print(ticker.ljust(8), f"ror : {ror:.2f}", f"기간수익률 : {기간수익률:.2f}")
print(df.index[0],'부터 ',df.index[-1],'까지')