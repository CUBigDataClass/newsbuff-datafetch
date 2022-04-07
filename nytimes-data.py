#"nytimes"

import csv
import datetime
import json
import sys
from datetime import datetime

import requests
from pymongo import errors
from pynytimes import NYTAPI
from sqlalchemy import false

import mongodb
import mongodbconfig

# Specify API key to fetch the data
myKey = mongodbconfig.newsapikey
nyt = NYTAPI(myKey, parse_dates=True)
currentTime = datetime.now()

# Function definition to fetch the NY times Archive data for given month and year.
def getData(year, month):
    data = nyt.archive_metadata(
    date = datetime(year, month, 1))
    nyt.close()
    return data

def clearOutputFile():
    with open("myArticleNoLocation.txt",'w') as f:
        pass
    with open("myArticleOneLocation.txt",'w') as f:
        pass
    with open("myArticleManyLocations.txt",'w') as f:
        pass


def extract_lat_long_via_location(location):
    latitude, longitude = None, None
    api_key = mongodbconfig.google_api_key
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    endpoint = f"{base_url}?address={location}&key={api_key}"
    r = requests.get(endpoint)
    if r.status_code not in range(200, 299):
        return None, None
    try:
        '''
        This try block incase any of our inputs are invalid. This is done instead
        of actually writing out handlers for all kinds of responses.
        '''
        results = r.json()['results'][0]
        latitude = results['geometry']['location']['lat']
        longitude = results['geometry']['location']['lng']
    except:
        pass
    return latitude, longitude

def main():
    
    client = mongodb.dbConnection()
    mydb = mongodb.createdb(client)
    
    mycol1 = mydb["customers1"]
    mycol2 = mydb["customers2"]
    mycol3 = mydb["customers3"]
    mycol4 = mydb["location"]

    # Looping to fetch the data repeatedly for specified period of time.
    for year in range(2019, 2020, 1):
        myArticleNoLocation = []
        myArticleOneLocation = []
        myArticleManyLocations = []
        exceptionData = []
        #myArticle.clear()    #Clearing out the list of dictionaries to append new data for every year.
        for month in range(1, 2, 1):
            print("Attempting to fetch data for year {year} and month {month}:".format(year = str(year), month = str(month)))

            try:
                clearOutputFile()
                startTime = datetime.now()
                articles = getData(year, month)
                print("No. of articles in {year} and {month} is {len}".format(year = str(year), month = str(month), len = str(len(articles))))
                for article in articles:
                    location=[]
                    dateTime = article["pub_date"]
                    dateTime = dateTime.isoformat()

                    if "subsection_name" in article.keys():
                        subsection_name = article['subsection_name']
                    else:
                        subsection_name = "null"

                    if "multimedia" in article.keys() and len(article['multimedia']) > 0:
                        imageURL = "https://www.nytimes.com/" + article['multimedia'][0]['url']
                    else:
                        imageURL = "null"

                    for keyword in article["keywords"]:
                        if keyword["name"] == "glocations":
                            location.append(keyword["value"])

                    # Extracting only needed attributes from each article.
                    # if(len(location) == 0):
                    #     myArticleNoLocation.append({"year": year, "month": month, "datetime":dateTime , 
                    #     "section":article['section_name'] , "subsection":subsection_name , 
                    #     "headline":article['abstract'] , "description":article['lead_paragraph'] , 
                    #     "location":location , "webURL":article['web_url'] , "imageURL":imageURL})
                    
                    # elif(len(location) == 1):

                    if(len(location) == 1):
                        request = mycol4.find({"location":{"$eq":location[0]}})
                        requests = list(request)
                        if(len(requests) == 0):
                            coordinates = extract_lat_long_via_location(location[0])
                            latitude = coordinates[0]
                            longitude = coordinates[1]
                            mycol4.insert_many([{"location": location[0], "latitude": latitude, "longitude": longitude}])
                        else:
                            latitude = requests[0]['latitude']
                            longitude = requests[0]['longitude']
                        
                        myArticleOneLocation.append({"year": year, "month": month, "datetime":dateTime , 
                                    "section":article['section_name'] , "subsection":subsection_name , 
                                    "headline":article['abstract'] , "description":article['lead_paragraph'] , 
                                    "location":location[0] , "latitude": latitude, "longitude": longitude,
                                    "webURL":article['web_url'] , "imageURL":imageURL})

                        # with open("geolocations.json", 'r', encoding='utf-8') as f:
                        #     geolocations = json.load(f)
                        #     for value in enumerate(geolocations):
                        #         if (value[1]["location"] == location):

                        #             myArticleOneLocation.append({"year": year, "month": month, "datetime":dateTime , 
                        #             "section":article['section_name'] , "subsection":subsection_name , 
                        #             "headline":article['abstract'] , "description":article['lead_paragraph'] , 
                        #             "location":location[0] , "latitude":, "longitude":,
                        #             "webURL":article['web_url'] , "imageURL":imageURL})
                    
                    else:
                        myArticleManyLocations.append({"year": year, "month": month, "datetime":dateTime , 
                        "section":article['section_name'] , "subsection":subsection_name , 
                        "headline":article['abstract'] , "description":article['lead_paragraph'] , 
                        "location":location , "webURL":article['web_url'] , "imageURL":imageURL})

                # file1 = open(r"myArticleNoLocation.txt","w+", encoding="utf-8")
                # file1.write(str(myArticleNoLocation))

                file2 = open(r"myArticleOneLocation.txt","w+", encoding="utf-8")
                file2.write(str(myArticleOneLocation))

                file3 = open(r"myArticleManyLocations.txt","w+", encoding="utf-8")
                file3.write(str(myArticleManyLocations))

                endTime = datetime.now()

            except:
                e  = sys.exc_info()
                #exceptionDetails is a list consisting of year, month, exception reason.
                exceptionData.append(year)
                exceptionData.append(month)
                exceptionData.append(e)

                print("Exception data", exceptionData)

                #Writing the failed calls details into FailedCalls.csv file
                with open('FailedCalls.csv', 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(exceptionData)
                f.close()

    try:
        # mycol1.insert_many(myArticleNoLocation)
        mycol2.insert_many(myArticleOneLocation)
        mycol3.insert_many(myArticleManyLocations)
        '''
        mycol1.insert_many(myArticleNoLocation, ordered=false)
        mycol2.insert_many(myArticleOneLocation, ordered=false)
        mycol3.insert_many(myArticleManyLocations, ordered=false)
        '''

    except errors.BulkWriteError as e:
        print(f"Articles bulk insertion error {e}")
    

    # print("Number of articles with No location:", len(myArticleNoLocation))
    print("Number of articles with One location:", len(myArticleOneLocation))
    print("Number of articles with Many locations:", len(myArticleManyLocations))
    print("Number of exceptions:", len(exceptionData))
    print(endTime-startTime)

if __name__ == "__main__":
    main()
