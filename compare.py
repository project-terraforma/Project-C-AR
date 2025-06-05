import requests 
import json
from geopy.distance import geodesic

def get_osm_coords(place_name):
    url = 'https://nominatim.openstreetmap.org/search'
    params = {
        "q": place_name + ", great mall", # can have a place like claire's,milpitas
        "format": "json",
        "limit": 1
    }

    headers = {
        "User-Agent": "YourAppName/1.0 (anshikaagarwal2005@gmail.com)"
    }

    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    if data:
        return [data[0]['lat'], data[0]['lon']]
    else:
        return None, None

with open("hi.geojson", "r") as file:
    content = file.read()
    # print(content)
    d = json.loads(content)
    load = d['features']
    for i in load:
        name = i['properties']['name']
        orig_coords = i['geometry']['coordinates']
        # print(orig_coords)
        # print(name)
        coords = get_osm_coords(name)
        if coords != orig_coords:
            print(name)

        
