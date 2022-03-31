from bson.json_util import dumps
from flask import Flask, request

import mongodb

app = Flask(__name__)

db_name = "testdbnewsbuff"
collection_name = "customers2"
@app.get("/newsbuff/<year>/<month>")
def get_news_year_month(year,month):
    try:
        client = mongodb.dbConnection()
        mydb = client[db_name]
        
        mycol2 = mydb[collection_name]
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

@app.get("/newsbuff/<location>")
def get_news_location(location):
    try:
        client = mongodb.dbConnection()
        mydb = client[db_name]
        
        mycol2 = mydb[collection_name]
        news = mycol2.find({
            "location":{"$eq":location},
        })
        print(news)
        l = list(news)
        for i in l:
            print(i)
    except Exception as e:
        print(e)

    return dumps(l)


@app.get("/newsbuff/<section>/<subsection>")
def get_news_section_subsection(yesectionar,subsection):
    try:
        client = mongodb.dbConnection()
        mydb = client[db_name]
        
        mycol2 = mydb[collection_name]
        news = mycol2.find({
            "year":{"$eq":section},
            "month":{"$eq":subsection}
        })
        print(news)
        l = list(news)
        for i in l:
            print(i)
    except Exception as e:
        print(e)

    return dumps(l)