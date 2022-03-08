#"nytimes"


from asyncio.windows_events import NULL
from pynytimes import NYTAPI
import datetime
import json
import sys
import time
import pandas
import pymongo
import mongodbconfig

# Specify API key to fetch the data
myKey = ""
nyt = NYTAPI(myKey, parse_dates=True)
currentTime = datetime.datetime.now()

# Function definition to fetch the NY times Archive data for given month and year.
def getData(year, month):
    data = nyt.archive_metadata(
    date = datetime.datetime(year, month, 1))
    nyt.close()
    return data


# Looping to fetch the data repeatedly for specified period of time.
myArticle = []
exceptionData = []
for year in range(2020, 2021, 1):
#    myArticle.clear()    #Clearing out the list of dictionaries to append new data for every year.
    for month in range(2, 4, 1):
        print("Attempting to fetch data for year {year} and month {month}:".format(year = str(year), month = str(month)))

        try:
            #print("Inside try block.")
            articles = getData(year, month)
            print("No. of articles in {year} and {month} is {len}".format(year = str(year), month = str(month), len = str(len(articles))))
            for article in articles:
                if "subsection_name" in article.keys():
                    subsection_name = article['subsection_name']
                else:
                    subsection_name = "null"

                if "multimedia" in article.keys() and len(article['multimedia']) > 0:
                    imageURL = article['multimedia'][0]['url']
                else:
                    imageURL = "null"

                for keyword in article["keywords"]:
                    if keyword["name"] == "glocations":
                        location = keyword["value"]
                        # Extracting only needed attributes from each article.
                        elements = {"datetime":article["pub_date"] , "section":article['section_name'] , "subsection":subsection_name , 
                        "headline":article['abstract'] , "description":article['lead_paragraph'] , "location":location , 
                        "webURL":article['web_url'] , "imageURL":imageURL}
                        myArticle.append(elements)

        except:
            e  = sys.exc_info()
            exceptionDetails = {"year": year, "month": month, "failureReason": e}
            exceptionData.append(exceptionDetails)



# Writing exception details to csv file
fileName = "FailedCalls.csv"

def getFailedCalls():
    if len(exceptionData) < 1:
        exceptionDict = {"runtime": currentTime, "exceptionDetails": "No failed calls in this run."}
    else:
        exceptionDict = {"runtime": currentTime, "exceptionDetails": exceptionData}
    return exceptionDict

file = open(fileName, 'a', newline='')
exceptions = getFailedCalls()
file.write(str(exceptions)+"\n")
file.close

print("Number of articles with g_locations:", len(myArticle))
print(myArticle[0])
print(exceptionData)
print("length of exception data:", len(exceptionData))

# Replace the uri string with your MongoDB deployment's connection string.
conn_str = "mongodb+srv://newsbuff:"+mongodbconfig.mongoDBPwd+"@newbuffcluster.j94k7.mongodb.net/test?retryWrites=true&w=majority"
# set a 5-second connection timeout
client = pymongo.MongoClient(conn_str, serverSelectionTimeoutMS=5000)
try:
    print(client.server_info())
except Exception:
    print("Unable to connect to the server.")