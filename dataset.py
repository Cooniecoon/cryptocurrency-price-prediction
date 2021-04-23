import tensorflow as tf
import os
import pathlib
import cv2
data_dir='./data/chart/day/'

data_dir = pathlib.Path(data_dir)
chart_imgs = list(data_dir.glob('*/*.jpg'))
print(len(chart_imgs))

def import_model():
    with tf.device("gpu:0"):
        model = Sequential()

        model.add(Conv2D(32, kernel_size=(3, 3), activation='relu', input_shape=(300,300,3)))
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
        model.add(Dense(1, activation='softmax'))
    return model



def get_chart_data(*paths):
    label_to_index = {'down':0,'up':1}
    for path in paths:
        path=str(path)
        path=path.replace('b','')
        path=path.replace('\'','')
        print('\n\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
        print('path : ',path.split('\\\\'))
        print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n\n')
        label=label_to_index[str(path).split('\\\\')[-2]]
        img=cv2.imread(str(path))
        img=cv2.resize(img,(300,300))
        print('label ',label)
        yield (img/255, label)


# gen = get_chart_data(data_dir)
# print(next(gen))


dataset = tf.data.Dataset.from_generator(get_chart_data,
                                         (tf.float32, tf.int8),
                                        (tf.TensorShape([300,300,3]), tf.TensorShape([])),
                                         args=[str(i) for i in chart_imgs])


for image, label in dataset.take(1):
    print("Image shape: ", image.numpy().shape)
    print("Label: ", label.numpy())


dataset = dataset.shuffle(150).batch(8)



model = import_model()

model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy',])
model.fit(dataset, epochs=10)
