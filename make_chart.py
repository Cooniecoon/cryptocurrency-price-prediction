from mpl_finance import candlestick2_ohlc
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import pandas as pd 
from datetime import datetime

dataset_path='./data/chart/minutes_240/'
df = pd.read_csv('./data/Upbit_BTC_240_Data.csv')

df['MA3'] = df['TradePrice'].rolling(3).mean()
df['MA5'] = df['TradePrice'].rolling(5).mean()
df['MA10'] = df['TradePrice'].rolling(10).mean()
df['MA20'] = df['TradePrice'].rolling(20).mean()


# index = [i.split('T')[0][2:] for i in list(df['Time'])] # 캔들스틱 x축
end_point=df.index.stop
term=30
idx=0
fig = plt.figure(figsize=(16,9))

up_count=0
down_count=0
top_axes = plt.subplot2grid((5,5), (0,0), rowspan=3, colspan=5)
bottom_axes = plt.subplot2grid((5,5), (3,0), rowspan=2, colspan=5, sharex=top_axes)
bottom_axes.get_yaxis().get_major_formatter().set_scientific(False)


plt.tight_layout(pad=0.0,h_pad=0.0,w_pad=0.0)
while True:
    
    top_axes.axis('off')
    bottom_axes.axis('off') 
    df_terminated=df.iloc[idx:idx+term]
    
    # index = [i.split('T')[0][2:] for i in list(df_terminated['Time'])] # 캔들스틱 x축
    index=df_terminated['Time']  
    # 이동평균선 그리기
    top_axes.plot(index, df_terminated['MA3'], label='MA3', linewidth=2)
    top_axes.plot(index, df_terminated['MA5'], label='MA5', linewidth=2)
    top_axes.plot(index, df_terminated['MA10'], label='MA10', linewidth=2)


    candlestick2_ohlc(top_axes, df_terminated['OpeningPrice'], df_terminated['HighPrice'], 
                    df_terminated['LowPrice'], df_terminated['TradePrice'],
                    width=0.7, colorup='r', colordown='b')
    
    color_fuc = lambda x : 'r' if x >= 0 else 'b'
    color_list = list(df_terminated['CandleAccTradeVolume'].diff().fillna(0).apply(color_fuc))
    bottom_axes.bar(index, df_terminated['CandleAccTradeVolume'], width=0.5, 
                    align='center',
                    color=color_list)

    
    next_price=df.iloc[idx+term]['TradePrice']
    current_price=df_terminated.iloc[-1]['TradePrice']

    if next_price>=current_price:
        up_count+=1
        plt.savefig(dataset_path+'up/ex_{}.png'.format(idx))
    elif next_price<current_price:
        down_count+=1
        plt.savefig(dataset_path+'down/ex_{}.png'.format(idx))

    print(f'up : {up_count},  down : {down_count},   total : {up_count+down_count}')

    top_axes.cla()
    bottom_axes.cla()
    
    idx+=1

    if idx+term>end_point-term:
        plt.close('all')
        break