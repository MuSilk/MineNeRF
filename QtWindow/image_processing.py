import os
import numpy as np
import json

import cv2

path = "../block_available"
files = os.listdir(path)

result = {}
id = 0

gamma = 1.8

for file in files:
    file_path = os.path.join(path, file)
    if os.path.isfile(file_path):
        name, suf = os.path.splitext(file)
        if suf == ".png":
            img = cv2.imread(file_path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            print(img)
            average_color_row = np.average(img, axis=0)
            average_color = np.average(average_color_row, axis=0)
            average_color = np.power(average_color / 255, gamma) * 255
            average_color=average_color.tolist()
            print(name + suf, average_color)

            result[id] = {
                'Name': "minecraft:" + name,
                'Color': average_color
            }
            id += 1

with open("../block_available/color_table.json", 'w') as file:
    json.dump(result, file, indent=4)
