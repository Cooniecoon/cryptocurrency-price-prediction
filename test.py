import math
import random

ox = [True, False]

seed = int(input("seed money : "))
init_buy = seed
profit_rate = int(input("benefit rate (%) : "))
loss_rate = int(input("loss rate (%) : "))
trade_num = int(input("trade num : "))
profit_rate/=100
loss_rate/=100

profit_num = 0
loss_num = 0
for i in range(trade_num):
    if random.choice(ox):
        profit_num+=1
        seed=seed*(1.0+profit_rate)
        print(i, 'PROFIT : ',seed)

    else:
        loss_num+=1
        seed=seed*(1.0-loss_rate)
        print(i, 'LOSS : ',seed)

print("tatal benefit : ",seed-init_buy)
print('Loss time : ',loss_num)
print('Gain time : ',profit_num)