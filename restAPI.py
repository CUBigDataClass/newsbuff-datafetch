from bson.json_util import dumps
from flask import Flask, request

import mongodb

app = Flask(__name__)

db_name = "testdbnewsbuff"
collection_name = "customers2"

@app.get("/newsbuff/time/<year>/<month>")
def get_news_year_month(year,month):
    response={}
    rows=[]
    try:
        client = mongodb.dbConnection()
        mydb = client[db_name]
        
        mycol2 = mydb[collection_name]
        request = mycol2.find({
            "year":{"$eq":int(year)},
            "month":{"$eq":int(month)}
        }).limit(20)
        articles = list(request)
        for article in articles:
            rows.append({"datetime":article['datetime'], "section":article['section'] ,"subsection":article['subsection'],
            "headline":article['headline'], "description":article['description'], "location":article['location'],
            "webURL":article['webURL'], "imageURL":article['imageURL']})
        response = {"request": {"year": year, "month": month}, "response": {"success": "true", "rows": rows}}

    except Exception as e:
        print(e)
        response = {"request": {"year": year, "month": month}, "response": {"success": "false"}}

    return dumps(response)

@app.get("/newsbuff/location/<location>")
def get_news_location(location):
    response={}
    rows=[]
    try:
        client = mongodb.dbConnection()
        mydb = client[db_name]
        
        mycol2 = mydb[collection_name]
        request = mycol2.find({"location":{"$eq":location}}).limit(20)
        articles = list(request)
        for article in articles:
            rows.append({"datetime":article['datetime'], "section":article['section'] ,"subsection":article['subsection'],
            "headline":article['headline'], "description":article['description'], "location":article['location'],
            "webURL":article['webURL'], "imageURL":article['imageURL']})
        response = {"request": {"location":location}, "response": {"success": "true", "rows": rows}}

    except Exception as e:
        print(e)
        response = {"request": {"location":location}, "response": {"success": "false"}}

    return dumps(response)


@app.get("/newsbuff/section_subsection/<section>/<subsection>")
def get_news_section_subsection(section,subsection):
    response={}
    rows=[]
    try:
        client = mongodb.dbConnection()
        mydb = client[db_name]
        
        mycol2 = mydb[collection_name]
        request = mycol2.find({
            "section":{"$eq":section},
            "subsection":{"$eq":subsection}
        }).limit(20)
        articles = list(request)
        for article in articles:
            rows.append({"datetime":article['datetime'], "section":article['section'] ,"subsection":article['subsection'],
            "headline":article['headline'], "description":article['description'], "location":article['location'],
            "webURL":article['webURL'], "imageURL":article['imageURL']})
        response = {"request": {"section": section, "subsection": subsection}, "response": {"success": "true", "rows": rows}}

    except Exception as e:
        print(e)
        response = {"request": {"section": section, "subsection": subsection}, "response": {"success": "false"}}

    return dumps(response)

#[ [ [ 0, 0 ], [ 3, 6 ], [ 6, 1 ], [ 0, 0 ] ] ]
@app.get("/newsbuff/polygon/<polygon>")
def get_news_polygon(polygon):
    response={}
    rows=[]
    try:
        client = mongodb.dbConnection()
        mydb = client[db_name]
        polygon = list(polygon)
        print(polygon)
        mycol2 = mydb[collection_name]
        request = mycol2.find({"location": { "$geoWithin": { "$geometry": { "type" : "Polygon", "coordinates" : polygon }}}}).limit(20)
        articles = list(request)
        for article in articles:
            rows.append({"datetime":article['datetime'], "section":article['section'] ,"subsection":article['subsection'],
            "headline":article['headline'], "description":article['description'], "location":article['location'],
            "webURL":article['webURL'], "imageURL":article['imageURL']})
        response = {"request": {"polygon": polygon}, "response": {"success": "true", "rows": rows}}

    except Exception as e:
        print(e)
        response = {"request": {"polygon": polygon}, "response": {"success": "false"}}

    return dumps(response)

if __name__ == '__main__':
    app.run(debug=True)