from re import M
import os
from time import sleep

import requests
from urllib.parse import urlencode
from xml.etree.ElementTree import fromstring, ElementTree
import zipfile
import io

from dotenv import load_dotenv

if os.path.exists(".env"):
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

def batch_geocode(addresses):
    url = "https://batch.geocoder.ls.hereapi.com/6.2/jobs?"
    query_params = {
        "apiKey": os.environ.get("GEOCODE_API_KEY"),
        "action": "run",
        "header": True,
        "inDelim": "|",
        "outDelim": "|",
        "outCols": "latitude,longitude",
        "outputCombined": True
    }
    data = "street|city|country\n"
    for street in addresses["streets"]:
        address_parts = [street, addresses["city"], addresses["country"]]
        line = "|".join(address_parts) + "\n"
        data += line

    headers = {
        "Content-Type": "text/plain",
        "charset": "UTF-8"
    }

    r = requests.post(url + urlencode(query_params), data=data.encode("utf-8"), headers=headers)
    
    if r.status_code != 200:
        return None
    
    xml_tree = ElementTree(fromstring(r.content))
    root = xml_tree.getroot()
    request_id = root[0][0][0].text
    status = root[0][1].text

    while status != "completed":
        sleep(1)
        status = get_batch_job_status(request_id)
        if status == "error":
            return None
    
    coords_list = get_batch_job_results(request_id)
    return coords_list

def get_batch_job_status(request_id):
    url = f"https://batch.geocoder.ls.hereapi.com/6.2/jobs/{request_id}?"
    query_params = {
        "apiKey": os.environ.get("GEOCODE_API_KEY"),
        "action": "status"
    }
    r = requests.get(url + urlencode(query_params))
    
    if r.status_code != 200:
        return "error"
    xml_tree = ElementTree(fromstring(r.content))
    root = xml_tree.getroot()
    status = root[0][1].text
    return status

def get_batch_job_results(request_id):
    url = f"https://batch.geocoder.ls.hereapi.com/6.2/jobs/{request_id}/result?"
    query_params = {
        "apiKey": os.environ.get("GEOCODE_API_KEY")
    }
    r = requests.get(url + urlencode(query_params), stream=True)

    if r.status_code != 200:
        return None
    
    z = zipfile.ZipFile(io.BytesIO(r.content))
    result = z.read(z.namelist()[0]).decode("utf-8")
    
    lines = result.split("\n")[1:-1]
    coords_list = []

    should_be_req_id = 1
    for line in lines:
        cols = line.split("|")
        req_id = int(cols[0])
        if req_id == should_be_req_id:
            coords_list.append((float(cols[3]), float(cols[4])))
            should_be_req_id += 1
    return coords_list
    

if __name__ == "__main__":
    addresses = {
        "country": "KAZ",
        "city": "Astana",
        "streets": [
            "ул. Бейбитшилик, 40",
            "пр. Республики, 2/1",
            "ул. Бейбитшилик, 40",
            "пр. Абылай хана, д. 31"
        ]
    }
    print(batch_geocode(addresses))