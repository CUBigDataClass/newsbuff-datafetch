from flask import Flask, request, Response
from flask_cors import CORS
import json
from bson import ObjectId
from datetime import datetime, timedelta
import pymongo
import mongodb

app = Flask(__name__)
CORS(app)

client = mongodb.dbConnection()
mydb = mongodb.createdb(client)
articleCollection = mydb["article"]
locationCollection = mydb["location"]
class MongoDbEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat() + 'Z'
        if isinstance(obj, ObjectId):
            return str(obj)
        return json.JSONEncoder.default(self, obj)

@app.get("/api/<year>/<month>/<day>")
def get_articles(year, month, day):
    params = request.args
    location = None
    sections = None
    try:
        startDate = datetime(int(year), int(month), int(day))
        endDate = startDate + timedelta(days=1)
    except:
        return Response(
            json.dumps({ "success": True, "count": 0, "rows": [] }),
            mimetype='application/json'
        )

    query = { "dateTime": { "$gte": startDate, "$lt": endDate } }
    if 'polygon' in params:
        polygon = json.loads(params['polygon'])
        # polygon = [ [ [ 0 , 0 ] , [ 3 , 6 ] , [ 6 , 1 ] , [ 0 , 0  ] ] ]
        query['locations'] = { '$elemMatch': {'location': { '$geoWithin': { '$geometry': { 'type': 'Polygon', 'coordinates': polygon } } } } }
    results = articleCollection.find(query, {'_id': False}).sort('dateTime', pymongo.DESCENDING).limit(100)
    resultsList = list(results)
    resultsCount = len(resultsList)
    return Response(
        json.dumps({ "success": True, "count": resultsCount, "rows": resultsList }, cls=MongoDbEncoder),
        mimetype='application/json'
    )

if __name__ == '__main__':
    app.run(debug=True)
