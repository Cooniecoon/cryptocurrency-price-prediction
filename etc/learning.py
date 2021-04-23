import pandas as pd
import numpy as np
import datetime
import pyupbit
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dropout, Dense, Activation
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.losses import Huber
from tensorflow.keras.optimizers import Adam
import datetime
import requests
from bs4 import BeautifulSoup


"""
time_units = ["days", "weeks"]
minutes_units = [1, 3, 5, 15, 30, 60, 240]
"""


def crawller(code, time):
    req = requests.get(
        f"https://crix-api-endpoint.upbit.com/v1/crix/candles/minutes/{time}?code=CRIX.UPBIT.KRW-{code}&count=400"
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


def normalize_windows(data):
    normalized_data = []
    for window in data:
        normalized_window = [((float(p) / float(window[0])) - 1) for p in window]
        # normalized_window = [((float(p) - min(window))/(max(window)-min(window))) for p in window]
        normalized_data.append(normalized_window)
    return np.array(normalized_data)


def load_price_info(code, interval, count=200):
    df = pyupbit.get_ohlcv(code, interval, count)
    df["Time"] = 0
    time_idx = list(df.index)
    for time, idx in enumerate(time_idx):
        df["Time"][idx] = str(idx)
    return df


def input_reshape(data):
    data = np.array(data)
    return np.reshape(data, (data.shape[0], data.shape[1], 1))

def model():
    with tf.device("gpu:0"):
        model = Sequential()

        # model.add(LSTM(seq_len, return_sequences=True, input_shape=(seq_len, 1)))

        # model.add(LSTM(64, return_sequences=True))
        # model.add(LSTM(32, return_sequences=False))

        # model.add(Dense(32, activation="linear"))
        # model.add(Dense(1, activation="linear"))

        model.add(LSTM(32, return_sequences=True, input_shape=(seq_len, 1)))
        model.add(Dropout(rate=0.2))

        model.add(LSTM(64, return_sequences=True))
        model.add(Dropout(0.2))

        model.add(LSTM(32, return_sequences=False))
        model.add(Dense(1))
    return model
code = "KRW-BTC"

data_path = ".\\data\\DOT_KRW_15_2021_3_5_11_20_46.csv"

time_units = ["15"]
for time_min in time_units:
    INTERVAL = "minute" + time_min

    # data = pd.read_csv(data_path)
    data = crawller(code[4:], time_min)
    data = data.sort_values(by=["Time"], axis=0)

    trade_prices = data["TradePrice"].values

    seq_len = 4 * 24
    sequence_length = seq_len + 1

    result = []
    for index in range(len(trade_prices) - sequence_length):
        result.append(trade_prices[index : index + sequence_length])

    result = normalize_windows(result)

    row = int(round(result.shape[0] * 0.9))
    train = result[:row, :]
    np.random.shuffle(train)

    x_train = train[:, :-1]
    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
    y_train = train[:, -1]

    x_test = result[row:, :-1]
    x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))
    y_test = result[row:, -1]

    model = Sequential()

    # model.add(LSTM(seq_len, return_sequences=True, input_shape=(seq_len, 1)))

    # model.add(LSTM(64, return_sequences=True))
    # model.add(LSTM(32, return_sequences=False))

    # model.add(Dense(32, activation="linear"))
    # model.add(Dense(1, activation="linear"))

    model.add(LSTM(32, return_sequences=True, input_shape=(seq_len, 1)))
    model.add(Dropout(rate=0.2))

    model.add(LSTM(64, return_sequences=True))
    model.add(Dropout(0.2))

    model.add(LSTM(32, return_sequences=False))
    model.add(Dense(1))

    loss = Huber()
    optimizer = Adam(0.0001)
    early_stop = EarlyStopping(monitor="val_loss", patience=5)
    model.compile(loss=Huber(), optimizer=optimizer, metrics=["mse"])

    start_time = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

    model.fit(
        x_train,
        y_train,
        validation_data=(x_test, y_test),
        epochs=100,
        verbose=False,
        callbacks=[
            # ModelCheckpoint(
            #     ".\\models\\%s_eth.h5" % (start_time),
            #     monitor="val_loss",
            #     verbose=False,
            #     save_best_only=True,
            #     mode="auto",
            # ),
            ReduceLROnPlateau(
                monitor="val_loss", factor=0.2, patience=5, verbose=0, mode="auto"
            ),
            early_stop,
        ],
    )

    df = load_price_info(code, interval=INTERVAL, count=200)
    load_time = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

    current_prices = df["close"].values
    last_price = df["open"].values
    curr_price = current_prices[-1]
    current_prices[-1] = last_price[-1]

    time_len = 5

    new_data = []
    future_price = []
    for index in range(len(current_prices) - sequence_length):
        new_data.append(current_prices[index : index + sequence_length - 1])
    for i in range(time_len):
        windowed_current_prices = normalize_windows([new_data[-1 - i]])
        windowed_current_prices = input_reshape(windowed_current_prices)
        pred = model.predict(windowed_current_prices[-time_len:])
        origin_price = (pred + 1) * new_data[-1 - i][0]

        future_price.append(origin_price[0][0])

    future = (
        1 + (future_price[0] - current_prices[-1]) / current_prices[-1]
    )  # (+) : 가격 상승, (-) : 가격 하락

    now = 1 + (future_price[1] - current_prices[-2]) / current_prices[-2]
    past = 1 + (future_price[2] - current_prices[-3]) / current_prices[-3]

    print("\n\n")
    print(f"========{code}__{INTERVAL}========  window size : {seq_len}")
    print("data loaded time : ", load_time)
    print("Time Epoch : ", INTERVAL)
    print("future : ", future)
    print("now : ", now)
    print("past : ", past)

    print("now : ", curr_price)
    print("last epoch price : ", last_price[-1])
    print("pridicted price : ", future_price[0])
    print("\n\n")
