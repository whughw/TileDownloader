import math
import numpy as np
import cv2
import requests
from tqdm import tqdm
import random

import tile_utils
import distance_utils
from concurrent_helper import run_with_concurrent

nproc = 8
retry_limit = 10
timeout = 5

def format_url(datasource, tileX, dx, tileY, dy, zoom):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        'Referer': 'https://www.tianditu.gov.cn/',
        'Connection': 'keep-alive',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8'
    }
    supported_source = ['tianditu', 'google', 'bing', 'arcgis']
    if datasource not in supported_source:
        raise NotImplementedError("Unknown source {}. Supported source list: {}".format(datasource,
                                                                                        ".".join(supported_source)))
    url = None
    if datasource == 'tianditu':
        # max zoom 18
        url = "http://t%d.tianditu.gov.cn/DataServer?T=img_w&x=%d&y=%d&l=%d&tk=9a02b3cdd29cd346de4df04229797710" % \
              (random.randint(1, 4), tileX + dx, tileY + dy, zoom)
    if datasource == 'google':
        # max zoom 20
        url = "https://khms%d.google.com/kh/v=%s&src=app&x=%d&y=%d&z=%d" % \
              (random.randint(0, 3), "908", tileX + dx, tileY + dy, zoom)
    if datasource == 'bing':
        # max zoom 19
        url = "http://ecn.t%d.tiles.virtualearth.net/tiles/a%s.jpeg?g=0" % \
              (random.randint(0, 3), tile_utils.TileXYToQuadKey(tileX + dx, tileY + dy, zoom))
    if datasource == 'arcgis':
        # max zoom 19
        url = "http://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/%d/%d/%d" % \
              (zoom, tileY + dy, tileX + dx)
    return url, headers

def download(url, headers, x, y, canvas, pbar):
    pbar.update(1)
    response = None
    retry = 0
    while response is None or response.status_code != 200:
        if retry == retry_limit:
            print("Failed to get {} with retry={}.".format(url, retry))
            return -1
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
        except Exception as e:
            pass
        retry += 1
    try:
        input_image_data = response.content
        np_arr = np.asarray(bytearray(input_image_data), np.uint8).reshape(1, -1)
        tile = cv2.imdecode(np_arr, cv2.IMREAD_UNCHANGED)
        # tile = tile.transpose((1,0,2))
        canvas[y * 256:(y + 1) * 256, x * 256:(x + 1) * 256, :] = tile
    except Exception as e:
        print(str(e))
        return -1
    return 0

def get_poi(lng, lat, datasource='google', dlng=0.1, dlat=0.1, zoom=18):
    center_lng = lng
    center_lat = lat
    dlng = distance_utils.lng_km2degree(dis_km=dlng, center_lat=lat)
    dlat = distance_utils.lat_km2degree(dis_km=dlat)
    # 仅适用于东北半球！
    tileX_tl, tileY_tl = tile_utils.lnglatToTile(center_lng - dlng, center_lat + dlat, zoom)
    tileX_br, tileY_br = tile_utils.lnglatToTile(center_lng + dlng, center_lat - dlat, zoom)
    nX = tileX_br - tileX_tl + 1
    nY = tileY_br - tileY_tl + 1
    canvas = np.zeros((nY*256, nX*256, 3), dtype=np.uint8)

    with tqdm(total=nX*nY) as pbar:
        task_list = []
        for x in range(nX):
            for y in range(nY):
                url, headers = format_url(datasource, tileX_tl, x, tileY_tl, y, zoom)
                task_list.append([url, headers, x, y, canvas, pbar])
        status = run_with_concurrent(download, task_list, "thread", min(nproc, len(task_list)))
    retry_list = []
    for i in range(len(status)):
        if status[i] != 0:
            retry_list.append(task_list[i])
    status = run_with_concurrent(download, retry_list, "thread", min(nproc, len(retry_list)))

    # cv2.imwrite("{}_{}.jpg".format(datasource, zoom), canvas)
    return canvas

if __name__ == '__main__':
    get_poi(116.26729497808765, 40.038987004118766, dlng=0.5, dlat=0.5, zoom=20)

    # # 故宫 [116.39092441666666, 39.91578330555556]
    # tileX_tl, tileY_tl = tile_utils.lnglatToTile(116.38558133333333, 39.921236, z)
    # tileX_br, tileY_br = tile_utils.lnglatToTile(116.39583333333333, 39.911944444444444, z)
    # nX = tileX_br - tileX_tl + 1
    # nY = tileY_br - tileY_tl + 1
    # canvas = np.zeros((nY*256, nX*256, 3), dtype=np.uint8)
    #
    # datasource = "google"
    # with tqdm(total=nX*nY) as pbar:
    #     task_list = []
    #     for x in range(nX):
    #         for y in range(nY):
    #             url, headers = format_url(datasource, tileX_tl, x, tileY_tl, y, z)
    #             task_list.append([url, headers, x, y, canvas, pbar])
    #     run_with_concurrent(download, task_list, "thread", min(nproc, len(task_list)))
    # cv2.imwrite("{}_{}.jpg".format(datasource, z), canvas)

    # # 天地图
    # print("http://t%d.tianditu.gov.cn/DataServer?T=img_w&x=%d&y=%d&l=%d&tk=9a02b3cdd29cd346de4df04229797710" % (0, tileX, tileY, z))
    # # google
    # print("https://khms%d.google.com/kh/v=%s&src=app&x=%d&y=%d&z=%d" % (1, "908", tileX, tileY, z))  # version: https://maps.googleapis.com/maps/api/js   https://khms\d+.googleapis\.com/kh\?v=(\d+)
    # print("http://mt3.google.cn/vt/lyrs=s@110&x=%d&y=%d&z=%d" % (tileX, tileY, z))  # z20
    # # yandex
    # # print("https://sat01.maps.yandex.net/tiles?l=sat&scale=1&lang=ru_RU&x=%d&y=%d&z=%d" % (tileX, tileY, z))
    # # bing
    # print("http://ecn.t0.tiles.virtualearth.net/tiles/a%s.jpeg?g=0" % (TileXYToQuadKey(tileX, tileY, z)))
    # # ArcGIS
    # print("http://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/%d/%d/%d" % (z, tileY, tileX))