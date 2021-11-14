import math
import numpy as np


# 像素分辨率
def getResolution(level):
    return 156543.03 * math.pow(2, -level)


# 经纬度转瓦片
def lnglatToTile(lng, lat, level):
    tileX = int((lng + 180) / 360 * math.pow(2, level))
    tileY = int((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) * math.pow(2, level - 1))
    return tileX, tileY


# 瓦片转经纬度
def tileToLnglat(tileX, tileY, level):
    level -= 1
    lng = tileX / math.pow(2, level) * 360 - 180
    lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * tileY / math.pow(2, level)))))
    return lng, lat


# 经纬度转像素
def lnglatToPixel(lng, lat, level):
    pixelX = round((lng + 180) / 360 * math.pow(2, level) * 256 % 256)
    pixelY = round(
        (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / (2 * math.pi)) * math.pow(2,
                                                                                                                 level) * 256 % 256)
    return pixelX, pixelY


# 瓦片和像素转经纬度
def pixelToLnglat(tileX, tileY, pixelX, pixelY, level):
    lng = (tileX + pixelX / 256) / math.pow(2, level) * 360 - 180
    lat = math.degrees(math.atan(math.sinh(math.pi - 2 * math.pi * (tileY + pixelY / 256) / math.pow(2, level))))
    return lng, lat

# bing瓦片坐标转换
def TileXYToQuadKey(tileX, tileY, level):
    quadKey = ''
    for l in range(level):
        i = level - l
        digit = ord('0')
        mask = 1 << (i - 1)
        if (tileX & mask) != 0:
            digit += 1
        if (tileY & mask) != 0:
            digit += 2
        quadKey += chr(digit)
    return quadKey
