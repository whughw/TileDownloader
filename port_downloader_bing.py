import requests
import json
import os
import cv2
import csv

import tile_downloader
import geo_utils

dlng = 2
dlat = 2
save_path = "./port_downloads/"
os.makedirs(save_path, exist_ok=True)

with open("port.csv", mode="r", encoding="utf-8") as f:
    loc_list = csv.reader(f)
    # loc_list = [l.split(",") for l in loc_list[1:]]
    # loc_list = [[l[2], float(l[22]), float(l[23])] for l in loc_list]
    loc_list = [[float(l[1]), float(l[0])] for l in loc_list]

datasource = [
              # {'datasource': 'google', 'zoom': 19},
              {'datasource': 'bing', 'zoom': 19},
              # {'datasource': 'arcgis', 'zoom': 19}
              ]

start_idx = 0
end_idx = 500

# for idx in range(resume_idx, len(loc_list)):
for idx in range(start_idx, end_idx):
    try:
        loc = loc_list[idx]
        print("{} / {}".format(idx, len(loc_list)))
        lng, lat = loc[1], loc[0]
        for d in datasource:
            image = tile_downloader.get_poi(lng, lat, dlng=dlng, dlat=dlat, **d)
            cv2.imencode('.jpg', image)[1].tofile\
                (os.path.join(save_path, "{}_{}.jpg".format(str(idx), d['datasource'])))
    except Exception as e:
        print(str(e))
        continue