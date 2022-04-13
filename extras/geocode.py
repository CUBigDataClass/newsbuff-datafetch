import os, geocoder, json
from os.path import join, dirname
from dotenv import load_dotenv
dotenv_path = join(dirname(__file__), '../.env')
load_dotenv(dotenv_path)

bing_api_key = os.environ.get('BING_API_KEY', None)

# locations = ['PHILIPSE MANOR HALL (YONKERS, NY)', 'BALDWIN', 'GREAT NECK ESTATES, NY', 'Europe', 'North Pole']
locations = json.load(open('locations.json', 'r'))
# print(locations)

locations = locations[:50]

g = geocoder.bing(locations, method='batch', key=bing_api_key)
res = []
for result in g:
   res.append(result.latlng)
# print(res)
json.dump(res, open('locationres.json', 'w'), indent=2)
