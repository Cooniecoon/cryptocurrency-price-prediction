import matplotlib.image as mpimg
import pandas as pd
import numpy as np

def min_max_normalize_ochl(arr):

    highmax=max(df_terminated['HighPrice'])
    lowmin=min(df_terminated['LowPrice'])
    norm_factor=(highmax-lowmin)
    norm_arr=(np.array(arr)-lowmin)/norm_factor
    return norm_arr

def min_max_normalize_ma(arr):

    highmax=max(arr)
    lowmin=min(arr)
    norm_factor=(highmax-lowmin)
    norm_arr=(np.array(arr)-lowmin)/norm_factor
    return norm_arr

def make_chart(df_terminated,img_w,img_h,term,linewidth,alpha,colors):
    date_term=int(img_w/term)
    candle_width=date_term
    ma5=min_max_normalize_ma(df_terminated['MA5'])
    ma10=min_max_normalize_ma(df_terminated['MA10'])
    ma20=min_max_normalize_ma(df_terminated['MA20'])
    high=min_max_normalize_ochl(df_terminated['HighPrice'])
    low=min_max_normalize_ochl(df_terminated['LowPrice'])
    open=min_max_normalize_ochl(df_terminated['OpeningPrice'])
    close=min_max_normalize_ochl(df_terminated['TradePrice'])


    ma5=np.array(ma5*(img_h-1),dtype=np.int8)
    ma10=np.array(ma10*(img_h-1),dtype=np.int8)
    ma20=np.array(ma20*(img_h-1),dtype=np.int8)
    high=np.array(high*(img_h-1),dtype=np.int8)
    low=np.array(low*(img_h-1),dtype=np.int8)
    open=np.array(open*(img_h),dtype=np.int8)
    close=np.array(close*(img_h-1),dtype=np.int8)


    ma5=(img_h-1)-ma5
    ma10=(img_h-1)-ma10
    ma20=(img_h-1)-ma20
    high=(img_h-1)-high
    low=(img_h-1)-low
    open=(img_h-1)-open
    close=(img_h-1)-close

    # Draw Chart
    chart=np.zeros((img_h,img_w,3),dtype=np.int16)
    close_yesterday=0
    today=0
    for i in range(term):
        if close[i]>close_yesterday:
            color=colors['r']
        elif close[i]<close_yesterday:
            color=colors['b']
        elif close[i]==close_yesterday:
            color=colors['g']
        close_yesterday=close[i]

        # Draw high-low
        col_start=today+date_term//2-linewidth//2
        col_finish=today+date_term//2+linewidth//2
        chart[high[i]:low[i]+1,col_start:col_finish,color]=255*alpha

        # Draw open-close
        col_start=today+date_term//2-candle_width//2
        col_finish=today+date_term//2+candle_width//2
        chart[min(open[i],close[i]):max(open[i],close[i])+1,col_start:col_finish,color]=255*alpha

        # # Draw ma line
        # chart[ma5[i],today+date_term//2,:]=(255,255,0)
        # chart[ma10[i],today+date_term//2,:]=(255,0,255)
        # chart[ma20[i],today+date_term//2,:]=(0,255,255)
        # print(ma20[i])

        today+=date_term
    return chart


COIN_LIST=['BTC','BCH','BTG','BSV','BCHA','LTC','EOS','ETH','ETC','ZIL','ADA','XRP','DOT','XLM','ATOM']



img_w=80
img_h=60
term=20
linewidth=2
alpha=0.6
colors={'r':0,'b':2,'g':1}
train_val_split_rate=0.8

total=0
for coin in COIN_LIST:
    # for time_unit in ['day', '240']:
    for time_unit in ['day']:
        dataset_path=f'./data/chart/{time_unit}/'
        df = pd.read_csv(f'./data/price/Upbit_{coin}_{time_unit}_Data.csv')

        df['MA5'] = df['TradePrice'].rolling(5).mean()
        df['MA10'] = df['TradePrice'].rolling(10).mean()
        df['MA20'] = df['TradePrice'].rolling(20).mean()

        train_len=int(len(df)*train_val_split_rate)
        val_len=len(df)-train_len
        print(coin)
        print('total :',len(df),'train :',train_len,'  val :',val_len)

        df_train=df.iloc[0:train_len]
        df_val=df.iloc[train_len:]
        dataset={'train':df_train,'val':df_val}
        
        
        for key,df_sub in dataset.items():
            idx=0
            end_point=len(df_sub)

            up_count=0
            down_count=0
            
            while True:
                
                df_terminated=df_sub.iloc[idx:idx+term]

                idx+=1
                if idx+term>end_point-term:
                    break

                chart=make_chart(df_terminated,img_w,img_h,term,linewidth,alpha,colors)
                next_price=df.iloc[idx+term]['TradePrice']
                current_price=df_terminated.iloc[-1]['TradePrice']
                
                if next_price>=current_price:
                    up_count+=1
                    total+=1
                    path=dataset_path+key+'/up/{0}_{2}_{1}.jpg'.format(coin,idx,key)
                    arr=np.array(chart,dtype=np.uint8)
                    mpimg.imsave(path,arr)


                elif next_price<current_price:
                    down_count+=1
                    total+=1
                    path=dataset_path+key+'/down/{0}_{2}_{1}.jpg'.format(coin,idx,key)
                    arr=np.array(chart,dtype=np.uint8)
                    mpimg.imsave(path,arr)


            print(f'subset : {coin}_{key},   up : {up_count},  down : {down_count},   total : {total}')
    print('\n')       
