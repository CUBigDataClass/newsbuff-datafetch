#"nytimes"

import datetime
import sys
from datetime import datetime
from pydoc import cli

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

    for year in range(2019, 2020, 1):
        # Looping to fetch the data repeatedly for specified period of time.
        myArticleNoLocation = []
        myArticleOneLocation = []
        myArticleManyLocations = []
        exceptionData = []
        #myArticle.clear()    #Clearing out the list of dictionaries to append new data for every year.
        for month in range(1, 13, 1):
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
                    if(len(location) == 0):
                        myArticleNoLocation.append({"year": year, "month": month, "datetime":dateTime , 
                        "section":article['section_name'] , "subsection":subsection_name , 
                        "headline":article['abstract'] , "description":article['lead_paragraph'] , 
                        "location":location , 
                        "webURL":article['web_url'] , "imageURL":imageURL})
                    
                    elif(len(location) == 1):

                        coordinates = extract_lat_long_via_location(location[0])

                        myArticleOneLocation.append({"year": year, "month": month, "datetime":dateTime , 
                        "section":article['section_name'] , "subsection":subsection_name , 
                        "headline":article['abstract'] , "description":article['lead_paragraph'] , 
                        "location":location[0] , "latitude": coordinates[0], "longitude": coordinates[1],
                        "webURL":article['web_url'] , "imageURL":imageURL})
                    
                    else:
                        myArticleManyLocations.append({"year": year, "month": month, "datetime":dateTime , 
                        "section":article['section_name'] , "subsection":subsection_name , 
                        "headline":article['abstract'] , "description":article['lead_paragraph'] , "location":location , 
                        "webURL":article['web_url'] , "imageURL":imageURL})

                file1 = open(r"myArticleNoLocation.txt","w+", encoding="utf-8")
                file1.write(str(myArticleNoLocation))

                file2 = open(r"myArticleOneLocation.txt","w+", encoding="utf-8")
                file2.write(str(myArticleOneLocation))

                file3 = open(r"myArticleManyLocations.txt","w+", encoding="utf-8")
                file3.write(str(myArticleManyLocations))

                endTime = datetime.now()

            except:
                e  = sys.exc_info()
                exceptionDetails = {"year": year, "month": month, "failureReason": e}
                exceptionData.append(exceptionDetails)

    try:
        mycol1.insert_many(myArticleNoLocation,ordered=false, bypass_document_validation=True)
        mycol2.insert_many(myArticleOneLocation,ordered=false, bypass_document_validation=True)
        mycol3.insert_many(myArticleManyLocations,ordered=false, bypass_document_validation=True)

    except errors.BulkWriteError as e:
        print(f"Articles bulk insertion error {e}")


            

    # Writing exception details to csv file
    fileName = "FailedCalls.txt"

    def getFailedCalls():
        if len(exceptionData) < 1:
            exceptionDict = {"runtime": currentTime, "exceptionDetails": "No failed calls in this run."}
        else:
            exceptionDict = {"runtime": currentTime, "exceptionDetails": exceptionData}
        return exceptionDict

    # Write failed calls details into FailedCalls.json file
    exceptions = getFailedCalls()
    """
    with open('FailedCalls.json', mode='a+', encoding='utf-8') as f:
        json.dump(exceptions, f, ensure_ascii=False, indent=4, sort_keys=True, default=str)
        f.write(",")
    """

    file = open(fileName, 'a', newline='')
    file.write(str(exceptions)+"\n")
    file.close

    print(exceptionData)
    print("Number of articles with No location:", len(myArticleNoLocation))
    print("Number of articles with One location:", len(myArticleOneLocation))
    print("Number of articles with Many locations:", len(myArticleManyLocations))
    print("Number of exceptions:", len(exceptionData))
    print(endTime-startTime)

if __name__ == "__main__":
    main()
