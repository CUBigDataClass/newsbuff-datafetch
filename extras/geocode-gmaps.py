import os, json, requests
from os.path import join, dirname
from dotenv import load_dotenv
dotenv_path = join(dirname(__file__), '../.env')
load_dotenv(dotenv_path)

google_api_key = os.environ.get('GOOGLE_API_KEY', None)

def extract_lat_long_via_location(location):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    endpoint = f"{base_url}?address={location}&key={google_api_key}"
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
locations = json.load(open('locations.json', 'r'))
# print(locations)

start = 0
# end = 4
end = len(locations)
locations = locations[start:end]
for index, location in enumerate(locations):
    print(f"Fetching location {start + index}")
    res = extract_lat_long_via_location(location)
    op = f"{index},\"{location}\","
    if res is None:
        op += "null,null"
    else:
        op += f"{res[0]},{res[1]}"
    with open('locationres.csv', 'a') as f:
        f.write(f"{op}\n")
