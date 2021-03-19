# 2. Изучить список открытых API. Найти среди них любое, требующее авторизацию (любого типа).
# Выполнить запросы к нему, пройдя авторизацию.
# Ответ сервера записать в файл.
import requests
import json
client_id = "3a3ccc31a6b47f27326e"
client_secret = "04eed28feac1408bd195a622bc9e4cb8"
concrete_params = {
    "client_id": client_id,
    "client_secret": client_secret
}
base_url ="https://api.artsy.net/api/tokens/xapp_token"
r = requests.post(base_url, params=concrete_params)
from pprint import pprint
pprint (r.text)

headers = {
    "X-XAPP-Token": r.json()['token']
}

url = "https://api.artsy.net/api/artworks"
r = requests.get(url, headers = headers)
pprint(r.json())


if r.ok:
    path = "some_artworks.json"
    with open(path, "w") as f:
        json.dump(r.json(),f)
