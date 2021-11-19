import requests
import json
import os
import cv2
import csv

import tile_downloader
import geo_utils
from argparse import ArgumentParser

dlng = 2
dlat = 2
save_path = "./railway_station_downloads/"
os.makedirs(save_path, exist_ok=True)

with open("railway_station.csv", mode="r", encoding="utf-8") as f:
    loc_list = csv.reader(f)
    # loc_list = [l.split(",") for l in loc_list[1:]]
    # loc_list = [[l[2], float(l[22]), float(l[23])] for l in loc_list]
    loc_list_ = []
    for l in loc_list:
        try:
            loc_list_.append([l[0], float(l[1]), float(l[2])])
        except:
            pass

loc_list = loc_list_

parser = ArgumentParser()
parser.add_argument(
    '--source', type=str, default=r"google")
parser.add_argument(
    '--start', type=int, default=0)
parser.add_argument(
    '--end', type=int, default=len(loc_list))
parser.add_argument(
    '--nproc', type=int, default=8)
args = parser.parse_args()

datasource = {
              "google": {'datasource': 'google', 'zoom': 19},
              "bing": {'datasource': 'bing', 'zoom': 19},
              "arcgis": {'datasource': 'arcgis', 'zoom': 19},
              "tianditu": {'datasource': 'tianditu', 'zoom': 18}
}

start_idx = args.start
end_idx = args.end

for idx in range(start_idx, end_idx):
    try:
        loc = loc_list[idx]
        print("{} / {}".format(idx, len(loc_list)))
        name, lng, lat = loc[0], loc[2], loc[1]
        lng, lat = geo_utils.bd09_wgs84(lng, lat)
        d = datasource[args.source]
        image = tile_downloader.get_poi(lng, lat, dlng_km=dlng, dlat_km=dlat, nproc=args.nproc, **d)
        if image is None:
            print("Skip image {} with too many failures.".format(str(idx)))
            continue
        cv2.imencode('.jpg', image)[1].tofile\
            (os.path.join(save_path, "{}_{}_{}.jpg".format(name, str(idx), d['datasource'])))
    except Exception as e:
        print(str(e))
        continue