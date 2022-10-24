import requests
import os
from urllib.parse import urlencode
from dotenv import load_dotenv


load_dotenv()

def geocode(address):
    url = "https://geocode.search.hereapi.com/v1/geocode?"
    query_params = {
        "apiKey": os.environ.get("GEOCODE_API_KEY"),
        "q": address
    }

    r = requests.get(url + urlencode(query_params))
    if r.status_code != 200:
        return None
    
    position = r.json()["items"][0]["position"]

    return position["lat"], position["lng"]

if __name__ == "__main__":
    address = "Kazakhstan, Astana, ул. Бейбитшилик, 40"
    print(geocode(address))
