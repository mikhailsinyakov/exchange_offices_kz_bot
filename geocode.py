from re import M
import os
from time import sleep

import requests
from urllib.parse import urlencode

from dotenv import load_dotenv

if os.path.exists(".env"):
    load_dotenv()

def geocode(address):
    url = "https://geocoder.ls.hereapi.com/6.2/geocode.json?"
    query_params = {
        "apiKey": os.environ.get("GEOCODE_API_KEY"),
        "country": address["country"],
        "city": address["city"],
        "searchtext": address["street"]
    }

    r = requests.get(url + urlencode(query_params))
    if r.status_code != 200:
        return None
    
    try:
        position = r.json()["Response"]["View"][0]["Result"][0]["Location"]["DisplayPosition"]
        coords = position["Latitude"], position["Longitude"]
        return coords
    except (KeyError, IndexError):
        return None
