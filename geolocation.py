#! /usr/bin/env python3
import json

import requests

import mongodbconfig

# configure constant variables
JSON_FILENAME = "locations.json"

def extract_lat_long_via_location(location):
    latitude, longitude = None, None
    api_key = mongodbconfig.google_api_key
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    endpoint = f"{base_url}?address={location}&key={api_key}"
    r = requests.get(endpoint)
    if r.status_code not in range(200, 299):
        return None, None
    try:
        '''
        This try block incase any of our inputs are invalid. This is done instead
        of actually writing out handlers for all kinds of responses.
        '''
        results = r.json()['results'][0]
        latitude = results['geometry']['location']['lat']
        longitude = results['geometry']['location']['lng']
    except:
        pass
    return latitude, longitude

def main():
    with open(JSON_FILENAME, 'r', encoding='utf-8') as f:
        locations = json.load(f)
        location = []

        for value in enumerate(locations):
            coordinates = extract_lat_long_via_location(value[1])
            location.append({"location": value[1], "latitude": coordinates[0], "longitude": coordinates[1]})

        with open('geolocations.json', 'w', encoding='utf-8') as f:
            json.dump(location, f, indent=4)

if __name__ == "__main__":
    main()
