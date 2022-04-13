from flask import Flask, request, Response
import json
from datetime import datetime, timedelta
import mongodb

app = Flask(__name__)
client = mongodb.dbConnection()
mydb = mongodb.createdb(client)
articleCollection = mydb["article"]
locationCollection = mydb["location"]
class MongoDbEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat() + 'Z'
        return json.JSONEncoder.default(self, obj)

@app.get("/api")
def get_articles():
    params = request.args
    startDate = None
    endDate = None
    try:
        startDate = datetime.strptime(params['startDate'], "%Y-%m-%d")
        endDate = datetime.strptime(params['endDate'], "%Y-%m-%d") + timedelta(days=1)
    except:
        return Response(status=400)

    results = articleCollection.find({ "dateTime": { "$gte": startDate, "$lt": endDate } }, {'_id': False}).limit(20)
    return Response(
        json.dumps({ "success": True, "rows": list(results) }, cls=MongoDbEncoder),
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