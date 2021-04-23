
import numpy as np
import pathlib
import cv2

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten,Input
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.layers import MaxPooling2D


def get_label_data(path):
    label_to_index = {'down':0,'up':1}
    # print(path.parts)
    label=label_to_index[path.parts[-2]]
    print(label)
    return label

def import_model():
    with tf.device("gpu:0"):
        model = Sequential()
        model.add(Input((300,300,3)))
        model.add(Conv2D(32, kernel_size=(3, 3), activation='relu')) #, input_shape=(300,300,3)
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
        model.add(Dense(2, activation='softmax'))
    return model

class DataGenerator(tf.keras.utils.Sequence):
    'Generates data for Keras'
    def __init__(self, list_IDs, labels, batch_size=32, dim=(32,32,32), n_channels=1,
                 n_classes=10, shuffle=True):
        'Initialization'
        self.dim = dim
        self.batch_size = batch_size
        self.labels = labels
        self.list_IDs = list_IDs
        self.n_channels = n_channels
        self.n_classes = n_classes
        self.shuffle = shuffle
        self.on_epoch_end()

    def __len__(self):
        'Denotes the number of batches per epoch'
        return int(np.floor(len(self.list_IDs) / self.batch_size))

    def __getitem__(self, index):
        'Generate one batch of data'
        # Generate indexes of the batch
        indexes = self.indexes[index*self.batch_size:(index+1)*self.batch_size]

        # Find list of IDs
        list_IDs_temp = [self.list_IDs[k] for k in indexes]

        # Generate data
        X, y = self.__data_generation(list_IDs_temp)

        return X, y

    def on_epoch_end(self):
        'Updates indexes after each epoch'
        self.indexes = np.arange(len(self.list_IDs))
        if self.shuffle == True:
            np.random.shuffle(self.indexes)

    def __data_generation(self, list_IDs_temp):
        'Generates data containing batch_size samples' # X : (n_samples, *dim, n_channels)
        # Initialization
        X = np.empty((self.batch_size, *self.dim, self.n_channels))
        y = np.empty((self.batch_size,self.n_classes), dtype=int)

        # Generate data
        for i, ID in enumerate(list_IDs_temp):
            # Store sample
            X[i,] = cv2.resize(cv2.imread(str(ID)),self.dim)

            # Store class
            a=[0,0]
            a[get_label_data(ID)]=1
            print(a)
            y[i] = get_label_data(ID)#a#get_label_data(ID)
            print('\nasdfasdfasdfsd : ',ID,'  label : ',y[i],'\n')


        return X, np.expand_dims(np.array(y,dtype=np.int8),axis=1)#tf.keras.utils.to_categorical(y, num_classes=self.n_classes)


data_dir='./data/chart/day/'

data_dir = pathlib.Path(data_dir)
chart_imgs = list(data_dir.glob('*/*.jpg'))
# label=get_label_data(chart_imgs)
print(len(chart_imgs))

# Parameters
params = {'dim': (300,300),
          'batch_size': 1,
          'n_classes': 2,
          'n_channels': 3,
          'shuffle': True}

# Datasets
# partition = chart_imgs # IDs
labels = [] # Labels


# Design model
model = import_model()

model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy',])
for partition in chart_imgs:
    # Generators
    training_generator = DataGenerator([partition], labels, **params)
    # validation_generator = DataGenerator(partition['validation'], labels, **params)
    # Train model on dataset
    model.fit_generator(training_generator,epochs=1)
