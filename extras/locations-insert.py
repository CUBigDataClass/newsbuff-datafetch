
import os, sys, inspect, json
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

import mongodb

client = mongodb.dbConnection()
mydb = mongodb.createdb(client)
locationCollection = mydb["location"]
locationObjects = json.load(open('locations-tr.json'))
# for location in locationObjects:
#     del location["index"]
print(len(locationObjects), locationObjects[0])
# locationCollection.insert_many(locationObjects, ordered=False)
# locationCollection.delete_many({})