import pyupbit
from time import sleep, localtime
from os import system
import argparse


def clear(dt=0.033):
    sleep(dt)
    system("cls")


def orderbook_bar(orderbook_units):
    global price
    global total_ask_size
    global total_bid_size

    norm_factor = 80

    sizes = []
    for orderbook_unit in orderbook_units:
        sizes.append(orderbook_unit.get("ask_size"))
    ask_min_size = min(sizes)
    ask_max_size = max(sizes)

    sizes = []
    for orderbook_unit in orderbook_units:
        sizes.append(orderbook_unit.get("bid_size"))
    bid_min_size = min(sizes)
    bid_max_size = max(sizes)

    print("\033[90m \033[91m" + "\t<매수 호가 - 호가 | 주문량 | 비율>\t" + "\033[0m")
    bid_prices = []
    bid_sizes = []
    for orderbook_unit in orderbook_units:
        bid_prices.append(orderbook_unit.get("bid_price"))
        bid_sizes.append(orderbook_unit.get("bid_size"))

    bid_prices.reverse()
    bid_sizes.reverse()
    for bid_price, bid_size in zip(bid_prices, bid_sizes):
        norm_bid_size = (
            (bid_size - bid_min_size) / (bid_max_size - bid_min_size) * norm_factor
        )
        print(
            "{0}\t{1} | {2:,} | {3:.2f}%".format(
                bid_price,
                "=" * int(norm_bid_size),
                round(bid_size, 3),
                bid_size / total_bid_size * 100,
            )
        )

    print("\n\n" + "\033[90m \033[36m" + "\t<매도 호가 - 호가 | 주문량 | 비율>\t" + "\033[0m")
    for orderbook_unit in orderbook_units:
        ask_price = orderbook_unit.get("ask_price")
        ask_size = orderbook_unit.get("ask_size")
        norm_ask_size = (
            (ask_size - ask_min_size) / (ask_max_size - ask_min_size) * norm_factor
        )
        print(
            "{0}\t{1} | {2:,} | {3:.2f}%".format(
                ask_price,
                "=" * int(norm_ask_size),
                round(ask_size),
                ask_size / total_ask_size * 100,
            )
        )


parser = argparse.ArgumentParser()
parser.add_argument("--code", type=str, default="BTC", help="coin code")
opt = parser.parse_args()

code = "KRW-" + opt.code

with open("secret_key.txt", "r") as f:
    access = f.readline().strip()
    secret = f.readline().strip()

upbit = pyupbit.Upbit(access, secret)


orderbook = pyupbit.get_orderbook(tickers=code)[0]
orderbook_units = orderbook["orderbook_units"]

price = pyupbit.get_current_price(code)

holding = upbit.get_balance(code)

buy_price = upbit.get_avg_buy_price(code)

now = localtime()

total_ask_size = orderbook["total_ask_size"]
total_bid_size = orderbook["total_bid_size"]

while True:
    print("종목 : {}".format(code))
    if total_ask_size > total_bid_size:
        print("\033[34m" + "매도량 우세" + "\033[0m", end="\n")
    else:
        print("\033[31m" + "매수량 우세" + "\033[0m", end="\n")

    print(
        "체결 강도 : {0:8.2f} %".format(total_bid_size / total_ask_size * 100),
        end="\n",
    )

    print("현재 가격 : " + "\033[33m" + "{0:8,} 원".format(price) + "\033[0m", end="\n")

    print("보유 수량 : {0:8,} 개".format(round(holding)), end="\n")

    print("평가 금액 : {0:8,} 원".format(round(holding * price)), end="\n")

    margin = round((price - buy_price) * holding)
    if margin > 0:
        print(
            "손익      : " + "\033[31m" + "{0:+8,} 원".format(margin) + "\033[0m",
            end="\n",
        )
    elif margin == 0:
        print("손익      : {0:+8,} 원".format(margin), end="\n")
    else:
        print(
            "손익      : " + "\033[34m" + "{0:+8,} 원".format(margin) + "\033[0m", end="\n"
        )

    if holding:
        margin_rate = round((price - buy_price) / buy_price * 100, 2)
        if margin_rate > 0:
            print(
                "수익률    : " + "\033[31m" + "{0:+8,} %".format(margin_rate) + "\033[0m",
                end="\n\n",
            )
        if margin_rate < 0:
            print(
                "수익률    : " + "\033[34m" + "{0:+8,} %".format(margin_rate) + "\033[0m",
                end="\n\n",
            )
    else:
        print(
            "수익률    : " + "{0:+8,} %".format(0),
            end="\n\n",
        )

    orderbook_bar(orderbook_units)

    print(
        "\n현재 시간 : %04d/%02d/%02d %02d:%02d:%02d"
        % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
    )

    orderbook = pyupbit.get_orderbook(tickers=code)[0]
    orderbook_units = orderbook["orderbook_units"]

    price = pyupbit.get_current_price(code)

    holding = upbit.get_balance(code)

    buy_price = upbit.get_avg_buy_price(code)

    now = localtime()

    total_ask_size = orderbook["total_ask_size"]
    total_bid_size = orderbook["total_bid_size"]

    clear()