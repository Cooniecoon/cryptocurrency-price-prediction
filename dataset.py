import tensorflow as tf
import matplotlib.pyplot as plt
import cv2
import numpy as np

from tensorflow.keras import layers
from tensorflow.keras.layers import Input, Dense, Conv2D, MaxPooling2D, Flatten, Dropout, Activation, add
from tensorflow.keras.models import Model, Sequential

from tensorflow.keras.optimizers import *

def CandleModel(SHAPE, nb_classes, seed=None):
    # We can't use ResNet50 directly, as it might cause a negative dimension
    # error.
    if seed:
        np.random.seed(seed)

    input_layer = Input(shape=SHAPE)

    # Step 1
    x = Conv2D(32, 3, 3 ,
               padding='same', activation='relu')(input_layer)
    # Step 2 - Pooling
    x = MaxPooling2D(pool_size=(2, 2))(x)

    # Step 1
    x = Conv2D(48, 3, 3 , padding='same',
               activation='relu')(x)
    # Step 2 - Pooling
    x = MaxPooling2D(pool_size=(2, 2))(x)
    x = Dropout(0.25)(x)

    # Step 1
    x = Conv2D(64, 3, 3 , padding='same',
               activation='relu')(x)
    # Step 2 - Pooling
    x = MaxPooling2D(pool_size=(2, 2))(x)

    # Step 1
    x = Conv2D(96, 3, 3 , padding='same',
               activation='relu')(x)
    # Step 2 - Pooling
    x = MaxPooling2D(pool_size=(2, 2))(x)
    x = Dropout(0.25)(x)

    # Step 3 - Flattening
    x = Flatten()(x)

    # Step 4 - Full connection

    x = Dense(output_dim=256, activation='relu')(x)
    # Dropout
    x = Dropout(0.5)(x)

    x = Dense(output_dim=2, activation='softmax')(x)

    model = Model(input_layer, x)

    return model

batch_size=16
img_height, img_width = 300, 400
channel = 3
epochs = 10
SHAPE = (img_width, img_height, channel)
def get_label(file_path):
    parts=str(file_path.numpy()).split('\\\\')[-2]
    path=str(file_path.numpy()).replace('\\\\','/')
    path=path.replace('b','')
    path=path.replace('\'','')
    # print(path)
    # The second to last is the class-directory
    one_hot = parts == class_names
    # Integer encode the label
    label = tf.argmax(one_hot)
    # img = cv2.imread(path)
    # img = cv2.resize(img,(img_width,img_height),interpolation=cv2.INTER_AREA)
    img = tf.io.read_file(file_path)
    img = decode_img(img)
    # img = decode_img(img)
    return img, label

def test(file_path):
    print(file_path.as_numpy_iterator())
    parts=str(file_path.as_numpy_iterator()).split('\\\\')[-2]
    path=str(file_path.as_numpy_iterator()).replace('\\\\','/')
    path=path.replace('b','')
    path=path.replace('\'','')
    # print(path)
    # The second to last is the class-directory
    one_hot = parts == class_names
    # Integer encode the label
    label = tf.argmax(one_hot)
    # img = cv2.imread(path)
    # img = cv2.resize(img,(img_width,img_height),interpolation=cv2.INTER_AREA)
    img = tf.io.read_file(file_path)
    img = decode_img(img)
    # img = decode_img(img)
    return img, label

def decode_img(img):
    # convert the compressed string to a 3D uint8 tensor
    img = tf.image.decode_png(img, channels=3)
    # resize the image to the desired size
    return tf.image.resize(img, [img_height, img_width])

def process_path(file_path):
    label = get_label(file_path)
    # load the raw data from the file as a string
    img = tf.io.read_file(file_path)
    img = decode_img(img)
    return img, label

# model=CandleModel(SHAPE, 2)
# print(model.summary)
# model.compile(
#     optimizer='adam',
#     loss=tf.losses.BinaryCrossentropy(from_logits=True),
#     metrics=['accuracy'])



data_dir='./data/chart/*/day/*/*.png'

list_ds = tf.data.Dataset.list_files(data_dir, shuffle=True)
f=list_ds.take(1)
print(str(list(f.as_numpy_iterator())[0]).split('\\')[-3])

class_names = np.array(['up','down'])
image_count = tf.data.experimental.cardinality(list_ds).numpy()

val_size = int(image_count * 0.2)
train_ds = list_ds.skip(val_size)
val_ds = list_ds.take(val_size)

print(tf.data.experimental.cardinality(train_ds).numpy())
print(tf.data.experimental.cardinality(val_ds).numpy())

AUTOTUNE = tf.data.experimental.AUTOTUNE
train_label=[]
# for f in val_ds.take(tf.data.experimental.cardinality(val_ds).numpy()):
#     # print(str(f.numpy()).split('\\')[-3])
    
#     train_label.append(get_label(f))


# train_ds = train_ds.map(get_label, num_parallel_calls=AUTOTUNE)
val_ds = val_ds.map(test, num_parallel_calls=AUTOTUNE)
# train_label=np.array(train_label)
# print(train_label.shape)

# for image, label in train_ds.take(1):
#     print("Image shape: ", image.numpy().shape)
#     print("Label: ", label.numpy())