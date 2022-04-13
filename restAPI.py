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

if __name__ == '__main__':
    app.run(debug=True)