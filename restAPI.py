import json
from flask import Flask, request, jsonify
import mongodbconfig
import mongodb
from bson.json_util import dumps

app = Flask(__name__)


@app.get("/newsbuff/<year>/<month>")
def get_news(year,month):
    try:
        client = mongodb.dbConnection()
        mydb = client['testdbnewsbuff']
        
        mycol2 = mydb["customers2"]
        news = mycol2.find({
            "year":{"$eq":int(year)},
            "month":{"$eq":int(month)}
        })
        print(news)
        l = list(news)
        for i in l:
            print(i)
    except Exception as e:
        print(e)

    return dumps(l)