import os, sys, inspect, json, requests
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

import env


def extract_lat_long_via_location(location):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    endpoint = f"{base_url}?address={location}&key={env.google_api_key}"
    r = requests.get(endpoint)
    if r.status_code not in range(200, 299):
        return None
    try:
        '''
        This try block incase any of our inputs are invalid. This is done instead
        of actually writing out handlers for all kinds of responses.
        '''
        results = r.json()['results'][0]
        latitude = results['geometry']['location']['lat']
        longitude = results['geometry']['location']['lng']
        return latitude, longitude
    except:
        return None


# locations = ['PHILIPSE MANOR HALL (YONKERS, NY)', 'BALDWIN', 'GREAT NECK ESTATES, NY', 'Europe', 'North Pole']
locations = json.load(open('locations1.json', 'r'))
# print(locations)

for index, location in enumerate(locations):
    res = extract_lat_long_via_location(location)
    op = f"{index},\"{location}\","
    if res is None:
        op += "null,null"
    else:
        op += f"{res[0]},{res[1]}"
    with open('location1res.csv', 'a') as f:
        f.write(f"{op}\n")
