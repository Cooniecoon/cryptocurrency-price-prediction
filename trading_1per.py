import threading
import queue
import time
import pyupbit
import datetime
from collections import deque

class Consumer(threading.Thread):
    def __init__(self, q):
        super().__init__()
        self.q = q
        self.ticker = "KRW-BTG"

        self.ma15 = deque(maxlen=15)
        self.ma50 = deque(maxlen=50)
        self.ma120 = deque(maxlen=90)

        df = pyupbit.get_ohlcv(self.ticker, interval="minute1")
        self.ma15.extend(df['close'])
        self.ma50.extend(df['close'])
        self.ma120.extend(df['close'])

        print(len(self.ma15), len(self.ma50), len(self.ma120))


    def run(self):    
        price_curr = None
        hold_flag = False
        wait_flag = False

        sell_ror=0.011
        buy_ror=1.01
        ma_threshold=1.0233

        with open("secret_key.txt", "r") as f:
            key0 = f.readline().strip()
            key1 = f.readline().strip()

        upbit = pyupbit.Upbit(key0, key1)
        cash  = upbit.get_balance()
        print("보유현금", cash)

        i = 0

        while True:   
            try:         
                if not self.q.empty():
                    if price_curr != None:
                        self.ma15.append(price_curr)
                        self.ma50.append(price_curr)
                        self.ma120.append(price_curr)

                    curr_ma15 = sum(self.ma15) / len(self.ma15)
                    curr_ma50 = sum(self.ma50) / len(self.ma50)
                    curr_ma120 = sum(self.ma120) / len(self.ma120)

                    price_open = self.q.get()
                    if hold_flag == False:
                        price_buy  = price_open * buy_ror
                        price_sell = price_open * (sell_ror+buy_ror)
                    wait_flag  = False

                price_curr = pyupbit.get_current_price(self.ticker)

                if hold_flag == False and wait_flag == False and \
                    price_curr >= price_buy and curr_ma15 >= curr_ma50 and \
                    curr_ma15 <= curr_ma50 * ma_threshold and curr_ma120 <= curr_ma50 :
                    # 0.05%
                    ret = upbit.buy_market_order(self.ticker, cash * 0.9995)
                    print("매수주문", ret)
                    time.sleep(1)
                    volume = upbit.get_balance(self.ticker)
                    ret = upbit.sell_limit_order(self.ticker, price_sell, volume)
                    print("매도주문", ret)
                    hold_flag = True
                # print(price_curr, curr_ma15, curr_ma50, curr_ma120)

                if hold_flag == True:
                    uncomp = upbit.get_order(self.ticker)
                    if len(uncomp) == 0:
                        cash = upbit.get_balance()
                        print("매도완료", cash)
                        hold_flag = False
                        wait_flag = True

                # 1 minutes
                if i==0 or i == (5 * 60 * 1):
                    print(f"[{datetime.datetime.now()}] 현재가 : {price_curr}, 목표가 : {price_buy}, \n조건1 (현재가 >= 목표가) : {price_curr >= price_buy}, 조건2 (ma15 <= ma50 * {ma_threshold}) : {curr_ma15 <= curr_ma50 * ma_threshold}, 조건3 (ma120 <= ma50) : {curr_ma120 <= curr_ma50}\n")
                    i = 0
                i += 1
            except:
                print("error")
                
            time.sleep(0.2)
            
class Producer(threading.Thread):
    def __init__(self, q):
        super().__init__()
        self.q = q

    def run(self):
        while True:
            price = pyupbit.get_current_price("KRW-BTG")
            self.q.put(price)
            time.sleep(60)            
            
q = queue.Queue()
Producer(q).start()
Consumer(q).start()