import sys
from math import *
from io import BytesIO
# Этот класс поможет нам сделать картинку из потока байт

import requests
from PIL import Image
from geo import map_size
from PIL import ImageFont, ImageDraw

# Пусть наше приложение предполагает запуск:
# python search.py Москва, ул. Ак. Королева, 12
# Тогда запрос к геокодеру формируется следующим образом:
toponym_to_find = " ".join('Москва, ул. Ак. Королева, 12')

geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

geocoder_params = {
    "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
    "geocode": toponym_to_find,
    "format": "json"}

response = requests.get(geocoder_api_server, params=geocoder_params)

if not response:
    # обработка ошибочной ситуации
    pass

# Преобразуем ответ в json-объект
json_response = response.json()
# Получаем первый топоним из ответа геокодера.
toponym = json_response["response"]["GeoObjectCollection"][
    "featureMember"][0]["GeoObject"]
# Координаты центра топонима:
toponym_coodrinates = toponym["Point"]["pos"]
# Долгота и широта:
toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
toponym_size = map_size(toponym)

######################################
search_api_server = "https://search-maps.yandex.ru/v1/"
api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

address_ll = toponym_longitude + ',' + toponym_lattitude

search_params = {
    "apikey": api_key,
    "text": "аптека",
    "lang": "ru_RU",
    "ll": address_ll,
    "type": "biz"
}

response = requests.get(search_api_server, params=search_params)

if not response:
    pass

###################################

# Преобразуем ответ в json-объект
json_response = response.json()

# Получаем первую найденную организацию.
organization = json_response["features"][:10]
# Название организации.
res = ",".join([toponym_longitude, toponym_lattitude, 'pm2am']) + ','
for i in organization:
    org_name = i["properties"]["CompanyMetaData"]["name"]
    timetable = i["properties"]["CompanyMetaData"]["Hours"]["text"]
    # Адрес организации.
    org_address = i["properties"]["CompanyMetaData"]["address"]

    # Получаем координаты ответа.
    point = i["geometry"]["coordinates"]
    org_point = "{0},{1}".format(point[0], point[1])
    delta = "0.005"
    # Собираем параметры для запроса к StaticMapsAPI:
    timetable = timetable.lower()
    if not timetable:
        res += "~{0},pm2grm".format(org_point) + ','
    elif '24' in timetable or 'круглосуточно' in timetable:
        res += "~{0},pm2gnm".format(org_point) + ','
    else:
        res += "~{0},pm2blm".format(org_point) + ','
res = res[:-1]
map_params = {
    "l": "map",
    "pt": res
}

map_api_server = "http://static-maps.yandex.ru/1.x/"
# ... и выполняем запрос
response = requests.get(map_api_server, params=map_params)

Image.open(BytesIO(
    response.content)).show()

# Создадим картинку
# и тут же ее покажем встроенным просмотрщиком операционной системы