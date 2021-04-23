import tensorflow as tf
import matplotlib.pyplot as plt
import cv2
import numpy as np
from os import listdir

from tensorflow.keras import layers
from tensorflow.keras.layers import Input, Dense, Conv2D, MaxPooling2D, Flatten, Dropout, Activation, add
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.optimizers import *
from sklearn.model_selection import train_test_split


def CandleModel(SHAPE, seed=None):
    # We can't use ResNet50 directly, as it might cause a negative dimension
    # error.
    if seed:
        np.random.seed(seed)
    with tf.device("gpu:0"):
        model = Sequential()

        model.add(Conv2D(32, kernel_size=(3, 3), activation='relu', input_shape=SHAPE))
        model.add(Conv2D(64, kernel_size=(3, 3), activation='relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(0.25))

        model.add(Conv2D(128, kernel_size=(3, 3), activation='relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Conv2D(128, kernel_size=(3, 3), activation='relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(0.25))

        model.add(Flatten())
        model.add(Dense(1024, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(3, activation='softmax'))

    return model


def build_dataset(data_directory='./data/chart/', coin_list=['BTC'], time_unit='day', input_wh=(400,300)):
    images_up = []
    images_down = []
    label=np.zeros((2),dtype=np.int8)
    for coin in coin_list:
        for file in listdir(f'{data_directory}/{coin}/{time_unit}/up'):
            if "jpg" in file.lower() or "png" in file.lower():
                img=cv2.imread(f'{data_directory}/{coin}/{time_unit}/up/' + file, cv2.IMREAD_COLOR)
                img=img/255.0
                img=cv2.resize(img,input_wh,interpolation=cv2.INTER_AREA)
                label[0]=1
                images_up.append((img,label))

    for coin in coin_list:
        for file in listdir(f'{data_directory}/{coin}/{time_unit}/down'):
            if "jpg" in file.lower() or "png" in file.lower():
                img=cv2.imread(f'{data_directory}/{coin}/{time_unit}/down/' + file, cv2.IMREAD_COLOR)
                img=img/255.0
                img=cv2.resize(img,input_wh,interpolation=cv2.INTER_AREA)
                label[1]=0
                images_down.append((img,label))

    return np.array(images_up),np.array(images_down)


COIN_LIST=['BTC']#,'BCH']#,'BTG','BSV','BCHA','LTC','EOS','ETH','ETC','ZIL','ADA','XRP','DOT','XLM','ATOM']
batch_size=16
epochs=5
img_up, img_down = build_dataset(coin_list=COIN_LIST)
dataset=np.concatenate((img_up, img_down))
np.random.shuffle(dataset)

X_data=dataset[:,0]
Y_data=dataset[:,1]

x_train, x_test, y_train, y_test = train_test_split(X_data, Y_data, test_size=0.2, random_state=42)

print('Train dataset : {0}\nTest dataset : {1}'.format(len(x_train),len(x_test)))


model = CandleModel(X_data[0].shape)
print(model.summary())


model.compile(optimizer=Adam(lr=1.0e-4),
                loss='categorical_crossentropy', metrics=['accuracy'])

# Fit the model
print(x_train[0])
model.fit(x_train, y_train,validation_data=(x_test,y_test), epochs=epochs)


predicted = model.predict(x_test)
y_pred = np.argmax(predicted, axis=1)
print(y_pred,y_test)
# save_path='/line_seg.weight'
# model.save_weights(save_path)