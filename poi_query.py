import requests
import json
import os
import cv2

import tile_downloader
import geo_utils

retry_limit = 5
poi_limit = 1
poi_offset = 20

def poi_api(url):
    response = None
    retry = 0
    while response is None or response.status_code != 200:
        if retry == retry_limit:
            print("Failed to get {} with retry={}.".format(url, retry))
            return
        try:
            response = requests.get(url, timeout=3)
        except Exception as e:
            retry += 1
    return response

dlng = 2
dlat = 2
save_path = "./downloads/"
os.makedirs(save_path, exist_ok=True)

url_templete = "https://restapi.amap.com/v3/place/text?key={}&keywords={}" \
               "&types=&city={}&children=&offset={}&page={}&extensions=all"
apikey = "f45e52a14a058319d3ba7b070f1db71d"
keywords = "机场"
type_constraint = ["飞机场"]
# city_list = "北京、天津、石家庄、邯郸、唐山、秦皇岛、张家口、太原、运城、长治、大同、吕梁、呼和浩特、包头、" \
#             "鄂尔多斯、海拉尔、赤峰、通辽、乌海、锡林浩特、满洲里、乌兰浩特、巴彦淖尔、加格达奇、二连浩特、" \
#             "阿拉善左旗、阿尔山、额济纳旗、阿拉善右旗、大连、沈阳、丹东、锦州、鞍山、朝阳、长海、长春、延吉、" \
#             "白山、通化、哈尔滨、牡丹江、佳木斯、大庆、齐齐哈尔、鸡西、黑河、漠河、伊春、抚远、上海、南京、" \
#             "无锡、常州、徐州、南通、扬州、连云港、盐城、淮安、杭州、温州、宁波、义乌、台州、舟山、衢州、" \
#             "合肥、黄山、阜阳、池州、安庆、厦门、福州、泉州、武夷山市、连城、南昌、赣州、景德镇、井冈山市、" \
#             "宜春、九江、青岛、济南、烟台、临沂、威海、济宁、潍坊、东营、郑州、洛阳、南阳、武汉、宜昌、襄阳、" \
#             "恩施、神农架、长沙、张家界、常德、怀化、永州、衡阳、广州、深圳、珠海、揭阳、湛江、梅州、南宁、" \
#             "桂林、北海、柳州、百色、梧州、河池、三亚、海口、重庆、万州、黔江、成都、松潘、绵阳、泸州、宜宾、" \
#             "南充、西昌 、达州、广元、攀枝花、稻城、康定、红原、贵阳、遵义、毕节、铜仁、兴义、安顺、凯里、" \
#             "黎平、荔波、六盘水、昆明、丽江、景洪、芒市、大理、腾冲、香格里拉、临沧、保山、普洱、昭通、文山、" \
#             "拉萨、林芝、昌都、阿里、日喀则、西安、榆林、延安、汉中、安康、兰州、敦煌、嘉峪关、庆阳、金昌、张掖、" \
#             "天水、夏河、西宁、格尔木、玉树、德令哈、银川、中卫、固原、乌鲁木齐、喀什、库尔勒、阿克苏、伊宁、和田、" \
#             "库车、哈密、阿勒泰、塔城、克拉玛依、博乐、布尔津、新源、吐鲁番、且末".split("、")
city_list = "安庆、厦门、福州、泉州、武夷山市、连城、南昌、赣州、景德镇、井冈山市、" \
            "宜春、九江、青岛、济南、烟台、临沂、威海、济宁、潍坊、东营、郑州、洛阳、南阳、武汉、宜昌、襄阳、" \
            "恩施、神农架、长沙、张家界、常德、怀化、永州、衡阳、广州、深圳、珠海、揭阳、湛江、梅州、南宁、" \
            "桂林、北海、柳州、百色、梧州、河池、三亚、海口、重庆、万州、黔江、成都、松潘、绵阳、泸州、宜宾、" \
            "南充、西昌 、达州、广元、攀枝花、稻城、康定、红原、贵阳、遵义、毕节、铜仁、兴义、安顺、凯里、" \
            "黎平、荔波、六盘水、昆明、丽江、景洪、芒市、大理、腾冲、香格里拉、临沧、保山、普洱、昭通、文山、" \
            "拉萨、林芝、昌都、阿里、日喀则、西安、榆林、延安、汉中、安康、兰州、敦煌、嘉峪关、庆阳、金昌、张掖、" \
            "天水、夏河、西宁、格尔木、玉树、德令哈、银川、中卫、固原、乌鲁木齐、喀什、库尔勒、阿克苏、伊宁、和田、" \
            "库车、哈密、阿勒泰、塔城、克拉玛依、博乐、布尔津、新源、吐鲁番、且末".split("、")
# keywords = "大桥"
# type_constraint = ["桥", "风景名胜"]
# city_list = "石渠 德格 白玉 巴塘 得荣 攀枝花 会东 宁南 金阳 布拖 雷波 屏山 高县 宜宾".split()
# city_list += "南溪 江安 长宁 泸州 合江".split()
# city_list += "德钦 香格里拉 丽江 玉龙 鹤庆 永胜 华坪 永仁 元谋 禄劝 巧家 鲁甸 昭通 永善 绥江 水富".split()
# city_list += "江津市 重庆 丰都 忠县 石柱 云阳 奉节 巫山".split()
# city_list += "巴东 秭归 宜昌 长阳 宜都 枝江 松滋 荆州 公安 江陵 石首 监利 洪湖 赤壁 " \
#              "嘉鱼 武汉 鄂州 团风 黄冈 浠水 蕲春 武穴 黄梅 黄石 阳新".split()
# city_list += "华容 岳阳 临湘".split()
# city_list += "宿松 望江 安庆 枞阳 东至 池州 铜陵 铜陵 无为 和县 繁昌 芜湖 当涂 马鞍山".split()
# city_list += "南京 仪征 扬州 江都 镇江 扬中 常州 泰州 泰兴 靖江 江阴 张家港 常熟 太仓 南通 海门 启东 上海".split()

for city in city_list:
    page = 1
    url = url_templete.format(apikey, keywords, city, poi_offset, page)
    response = poi_api(url)
    query_result = json.loads(response.content.decode("utf-8"))
    pois = query_result['pois']
    poi_count = int(query_result['count'])
    datasource = [{'datasource': 'google', 'zoom': 19}, {'datasource': 'tianditu', 'zoom': 18},
                  {'datasource': 'bing', 'zoom': 19}, {'datasource': 'arcgis', 'zoom': 19}]
    # datasource = [{'datasource': 'google', 'zoom': 17}, {'datasource': 'arcgis', 'zoom': 17}]
    for i in range(0, min(poi_count, poi_limit), 1):
        try:
            print("{} / {}".format(i+1, min(poi_count, poi_limit)))
            idx = i % poi_offset
            if (i // poi_offset + 1) != page:
                page += 1
                url = url_templete.format(apikey, keywords, city, poi_offset, page)
                response = poi_api(url)
                query_result = json.loads(response.content.decode("utf-8"))
                pois = query_result['pois']
            target_poi = pois[idx]
            location = target_poi['location']
            target_type = target_poi["type"]
            print(city)
            interested = False
            for constraint in type_constraint:
                if constraint in target_type:
                    interested = True
            if not interested:
                continue
            name = target_poi['name']
            lng, lat = map(float,location.split(','))
            lng, lat = geo_utils.gcj02_wgs84(lng, lat)
            for d in datasource:
                image = tile_downloader.get_poi(lng, lat, dlng=dlng, dlat=dlat, **d)
                cv2.imencode('.jpg', image)[1].tofile\
                    (os.path.join(save_path, "{}_{}.jpg".format(name, d['datasource'])))
                # cv2.imwrite(os.path.join(save_path, "{}_{}.jpg".format(i, d['datasource'])), image)
        except Exception as e:
            print(str(e))
            continue