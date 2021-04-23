from mpl_finance import candlestick2_ohlc
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import pandas as pd 
from datetime import datetime

# COIN_LIST=['BTC','BCH','BTG','BSV','BCHA','LTC',]
COIN_LIST=['BTC','BCH','BTG','BSV','BCHA','LTC','EOS','ETH','ETC','ZIL','ADA','XRP','DOT','XLM','ATOM']




for coin in COIN_LIST:
    for time_unit in ['day', '240']:
        fig = plt.figure(facecolor=(0,0,0),figsize=(6,6))
        top_axes = plt.subplot2grid((5,5), (0,0), rowspan=3, colspan=5)
        bottom_axes = plt.subplot2grid((5,5), (3,0), rowspan=2, colspan=5, sharex=top_axes)
        bottom_axes.get_yaxis().get_major_formatter().set_scientific(False)
        plt.tight_layout(pad=0.0,h_pad=0.0,w_pad=0.0)
        # plt.style.use(['dark_background'])
        

        dataset_path=f'./data/chart/{time_unit}/'
        df = pd.read_csv(f'./data/price/Upbit_{coin}_{time_unit}_Data.csv')

        df['MA3'] = df['TradePrice'].rolling(3).mean()
        df['MA5'] = df['TradePrice'].rolling(5).mean()
        df['MA10'] = df['TradePrice'].rolling(10).mean()
        df['MA20'] = df['TradePrice'].rolling(20).mean()

        # index = [i.split('T')[0][2:] for i in list(df['Time'])] # 캔들스틱 x축
        end_point=df.index.stop
        term=30
        idx=0
        

        up_count=0
        down_count=0
        while True:
            
            top_axes.axis('off')
            bottom_axes.axis('off') 
            df_terminated=df.iloc[idx:idx+term]
            
            # index = [i.split('T')[0][2:] for i in list(df_terminated['Time'])] # 캔들스틱 x축
            index=df_terminated['Time']  
            # 이동평균선 그리기
            top_axes.plot(index, df_terminated['MA3'], label='MA3', linewidth=1)
            top_axes.plot(index, df_terminated['MA5'], label='MA5', linewidth=1)
            top_axes.plot(index, df_terminated['MA10'], label='MA10', linewidth=1)


            candlestick2_ohlc(top_axes, df_terminated['OpeningPrice'], df_terminated['HighPrice'], 
                            df_terminated['LowPrice'], df_terminated['TradePrice'],
                            width=0.9, colorup='r', colordown='b',alpha=1)
            
            color_fuc = lambda x : 'r' if x >= 0 else 'b'
            color_list = list(df_terminated['CandleAccTradeVolume'].diff().fillna(0).apply(color_fuc))
            bottom_axes.bar(index, df_terminated['CandleAccTradeVolume'], width=0.7, 
                            align='center',
                            color=color_list,alpha=0.7)

            
            next_price=df.iloc[idx+term]['TradePrice']
            current_price=df_terminated.iloc[-1]['TradePrice']

            if next_price>=current_price:
                up_count+=1
                plt.savefig(dataset_path+'up/{0}_{1}.jpg'.format(coin,idx))
            elif next_price<current_price:
                down_count+=1
                plt.savefig(dataset_path+'down/{0}_{1}.jpg'.format(coin,idx))

            print(f'coin : {coin}_{time_unit},   up : {up_count},  down : {down_count},   total : {up_count+down_count}')

            top_axes.cla()
            bottom_axes.cla()
            
            idx+=1

            if idx+term>end_point-term:
                plt.close('all')
                break