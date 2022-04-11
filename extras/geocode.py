import geocoder, os, sys, inspect, json
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

import env

# locations = ['PHILIPSE MANOR HALL (YONKERS, NY)', 'BALDWIN', 'GREAT NECK ESTATES, NY', 'Europe', 'North Pole']
locations = json.load(open('locations.json', 'r'))
# print(locations)

locations = locations[:50]

g = geocoder.bing(locations, method='batch', key=env.bing_api_key)
res = []
for result in g:
   res.append(result.latlng)
# print(res)
json.dump(res, open('locationres.json', 'w'), indent=2)
