import json, sys
from datetime import datetime, timedelta

import pymongo
from bson import ObjectId
from flask import Flask, Response, request
from flask_cors import CORS
from flask_restx import Api, Resource
import mongodb

app = Flask(__name__)
CORS(app)

api = Api(app, 
		  version = "1.0", 
		  title = "News Buff Backend", 
		  description = "REST APIs for fetching news articles")

name_space = api.namespace('api', description='Main APIs')

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

@name_space.route("/ping")
class Class1(Resource):
    @api.doc(responses={ 200: 'OK' })
    def get(self):
        return Response(
            json.dumps({ "success": True }),
            mimetype='application/json'
        )

@name_space.route("/<int:year>/<int:month>/<int:day>")
class Class2(Resource):
    @api.doc(responses={ 200: 'OK', 400: 'Invalid parameters', 500: 'Something went wrong' }, 
            params={ 'year': 'Year', 'month': 'Month', 'day': 'Day',
                        'polygon': {'in': 'query', 'description': 'GeoJSON Polygon with a Single Ring'} })
    def get(self, year, month, day):
        params = request.args
        try:
            startDate = datetime(int(year), int(month), int(day))
            endDate = startDate + timedelta(days=1)
        except:
            errorInfo = sys.exc_info()
            print(errorInfo)
            return Response(
                json.dumps({ "success": False, "count": 0, "rows": [] }),
                mimetype='application/json'
            )

        try:
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
        except:
            errorInfo = sys.exc_info()
            print(errorInfo)
            return Response(
                json.dumps({ "success": False, "count": 0, "rows": [] }),
                mimetype='application/json'
            )

if __name__ == '__main__':
    app.run(debug=True)
