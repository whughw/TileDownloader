import requests
import json
import os
import cv2
import csv

import tile_downloader
import geo_utils

dlng = 2
dlat = 2
save_path = "./downloads/"
os.makedirs(save_path, exist_ok=True)

with open("Power_Plant.csv", mode="r", encoding="utf-8") as f:
    loc_list = csv.reader(f)
    # loc_list = [l.split(",") for l in loc_list[1:]]
    loc_list = [[l[2], float(l[15]), float(l[16])] for l in loc_list]

datasource = [
              # {'datasource': 'google', 'zoom': 19},
              # {'datasource': 'bing', 'zoom': 19},
              {'datasource': 'arcgis', 'zoom': 19}
              ]

start_idx = 4000
end_idx = 4500

# for idx in range(resume_idx, len(loc_list)):
for idx in range(start_idx, end_idx):
    try:
        loc = loc_list[idx]
        city = loc[0]
        print(city)
        print("{} / {}".format(idx, len(loc_list)))
        lng, lat = loc[2], loc[1]
        for d in datasource:
            image = tile_downloader.get_poi(lng, lat, dlng=dlng, dlat=dlat, **d)
            cv2.imencode('.jpg', image)[1].tofile\
                (os.path.join(save_path, "{}_{}_{}.jpg".format(city, str(idx), d['datasource'])))
    except Exception as e:
        print(str(e))
        continue