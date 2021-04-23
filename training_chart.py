import numpy as np
import cv2

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten,Input
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.layers import MaxPooling2D

def import_model(img_h, img_w):
    with tf.device("gpu:0"):
        model = Sequential([
        Input((img_h,img_w,3)),
        Conv2D(32, kernel_size=(3, 3), activation='relu'), #, input_shape=(300,300,3)
        Conv2D(64, kernel_size=(3, 3), activation='relu'),
        MaxPooling2D(pool_size=(2, 2)),
        Dropout(0.25),

        # Conv2D(128, kernel_size=(3, 3), activation='relu'),
        # MaxPooling2D(pool_size=(2, 2)),
        # Conv2D(128, kernel_size=(3, 3), activation='relu'),
        # MaxPooling2D(pool_size=(2, 2)),
        # Dropout(0.25),

        Flatten(),
        Dense(1024, activation='relu'),
        Dropout(0.5),
        Dense(2, activation='softmax')
        ]
        )
    return model


def get_label_data(path):
    label_to_index = {'down':0,'up':1}
    label=label_to_index[path.split('\\')[-2]]
    # print(label)
    return label

data_path='./data/chart/day'
batch_size=4
img_h, img_w = 300, 300


model = import_model(img_h, img_w)

model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy',])

idx=0
with open(data_path + "/train.txt", "r") as f:
        train_path=f.readlines()
        num_trainset=len(train_path)

with open(data_path + "/val.txt", "r") as f:
        val_path=f.readlines()

while True:
        
    train_batch=train_path[idx:idx+batch_size]
    val_batch=val_path[int(idx*0.2):int((idx+batch_size)*0.2)]
    print(train_batch)
    train_imgs=[]
    train_labels=[]
    for train_data in train_batch:
        img_data=train_data.replace('\n','')
        label=get_label_data(img_data)
        chart=cv2.imread(img_data)
        chart=cv2.resize(chart,(img_h,img_w))
        chart=chart/255
        train_imgs.append(chart)
        a=np.array([0,0])
        a[label]=1
        train_labels.append(a)
    train_imgs=np.array(train_imgs,dtype=np.float32)
    train_labels=np.array(train_labels,dtype=np.int8)

    # val_imgs=[]
    # val_labels=[]
    # for val_data in val_batch:
    #     img_data=val_data.replace('\n','')
    #     label=get_label_data(img_data)
    #     chart=cv2.imread(img_data)
    #     chart=cv2.resize(chart,(img_h,img_w))
    #     chart=chart/255
    #     val_imgs.append(chart)
    #     val_labels.append(label)
    # val_imgs=np.array(val_imgs,dtype=np.float32)
    # val_labels=np.array(val_labels,dtype=np.int8) 
    # print('\n\n\n',val_imgs.shape,train_imgs.shape)

    print('\n\n',train_imgs.shape, '   :   ',train_labels,'\n\n')

    model.fit(train_imgs, train_labels,batch_size=batch_size,  epochs=1)

    idx+=batch_size
    if idx>num_trainset:
        #! 
        break
















