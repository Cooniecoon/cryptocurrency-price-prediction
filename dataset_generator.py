from glob import glob
import pathlib
from sklearn.model_selection import train_test_split



data_path='./data/chart/day/'

data_dir = pathlib.Path(data_path)
chart_imgs = [str(i) for i in list(data_dir.glob('*/*.jpg'))]
print(type(chart_imgs[0]))

# dataset split
train_img_list, val_img_list = train_test_split(
    chart_imgs, test_size=0.2, random_state=2000
)

print("train_set : ", len(train_img_list), "validation_set : ", len(val_img_list))


# create train, validation dataset lists in textfile
with open(data_path + "/train.txt", "w") as f:
    f.write("\n".join(train_img_list) + "\n")

with open(data_path + "/val.txt", "w") as f:
    f.write("\n".join(val_img_list) + "\n")