import json

import requests


def upload_bb(img_url):
    url = "https://api.imgbb.com/1/upload"

    payload = {'key': '500363854a55a37ef82dafa38abd17c6',
               'expiration': '3600'}

    img_urls = img_url.split('/')

    img_file = open(img_url, "rb")
    files = [
        ('image', (img_urls[-1], img_file, 'image/jpeg'))
    ]
    headers = {}

    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    data = json.loads(response.text)
    print(data["data"]["url"])
    return data["data"]["url"]
