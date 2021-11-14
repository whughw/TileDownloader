import requests


query_keyword = "bridge"
inputtype = "textquery"
fields = "geometry"
key = "AIzaSyDQHx0hZhs_1X5EMp7lC1PHu15pulKsTUs"
url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?" \
      "input={}&inputtype={}&fields={}&key={}".format(query_keyword, inputtype, fields, key)

payload={}
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
