from flask import Flask, request, Response
from flask_cors import CORS
import json
from datetime import datetime, timedelta
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

    if 'location' in params:
        location = params['location']
        query['location'] = { "locations": { "$elemMatch" : { "location":  { "$eq": location} } } }
    if 'sections' in params:
        sections = params['sections']
        query['section'] = { "section": { "$in" : sections} }

    results = articleCollection.find(query, {'_id': False}).limit(30)
    resultsList = list(results)
    resultsCount = len(resultsList)
    return Response(
        json.dumps({ "success": True, "count": resultsCount, "rows": resultsList }, cls=MongoDbEncoder),
        mimetype='application/json'
    )

# #[ [ [ 0, 0 ], [ 3, 6 ], [ 6, 1 ], [ 0, 0 ] ] ]
# @app.get("/newsbuff/polygon/<polygon>")
# def get_news_polygon(polygon):
#     response={}
#     rows=[]
#     try:
#         client = mongodb.dbConnection()
#         mydb = client[db_name]
#         polygon = list(polygon)
#         print(polygon)
#         mycol2 = mydb[collection_name]
#         request = mycol2.find({"location": { "$geoWithin": { "$geometry": { "type" : "Polygon", "coordinates" : polygon }}}}).limit(20)
#         articles = list(request)
#         for article in articles:
#             rows.append({"datetime":article['datetime'], "section":article['section'] ,"subsection":article['subsection'],
#             "headline":article['headline'], "description":article['description'], "location":article['location'],
#             "webURL":article['webURL'], "imageURL":article['imageURL']})
#         response = {"request": {"polygon": polygon}, "response": {"success": "true", "rows": rows}}

#     except Exception as e:
#         print(e)
#         response = {"request": {"polygon": polygon}, "response": {"success": "false"}}

#     return dumps(response)


if __name__ == '__main__':
    app.run(debug=True)