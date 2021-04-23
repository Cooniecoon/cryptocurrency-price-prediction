from tensorflow.keras.preprocessing.image import ImageDataGenerator
import numpy as np
import cv2

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten,Input
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.layers import MaxPooling2D
sample_path='./data/sample/'

train=ImageDataGenerator(rescale=1/255)
train_dataset=train.flow_from_directory(sample_path,target_size=(300,300),batch_size=2,class_mode='binary')

print(train_dataset.class_indices)

with tf.device("gpu:0"):
    model = Sequential([
    Input((300,300,3)),
    Conv2D(32, kernel_size=(3, 3), activation='relu'), #, input_shape=(300,300,3)
    Conv2D(64, kernel_size=(3, 3), activation='relu'),
    MaxPooling2D(pool_size=(2, 2)),
    Dropout(0.25),

    Conv2D(128, kernel_size=(3, 3), activation='relu'),
    MaxPooling2D(pool_size=(2, 2)),
    Dropout(0.25),

    Flatten(),
    Dense(32, activation='relu'),
    Dropout(0.5),
    Dense(1, activation='softmax')
    ])
print(model.summary())

model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy',])

model.fit(train_dataset,epochs=10)

test_data_path=''

img=cv2.imread(test_data_path)
img=img/255
img=np.expand_dims(img,axis=0)
pred=model.predict(img)
print(pred)
print(train_dataset.class_indices[pred])
