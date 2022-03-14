#"nytimes"

import datetime
from pydoc import cli
import sys
from datetime import datetime

import pymongo
from pynytimes import NYTAPI

import mongodbconfig
import mongodb

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
                        imageURL = article['multimedia'][0]['url']
                    else:
                        imageURL = "null"

                    for keyword in article["keywords"]:
                        if keyword["name"] == "glocations":
                            location.append(keyword["value"])

                    # Extracting only needed attributes from each article.
                    if(len(location) == 0):
                        myArticleNoLocation.append({"datetime":dateTime , "section":article['section_name'] , "subsection":subsection_name , 
                        "headline":article['abstract'] , "description":article['lead_paragraph'] , "location":location , 
                        "webURL":article['web_url'] , "imageURL":imageURL})
                    
                    elif(len(location) == 1):
                        myArticleOneLocation.append({"datetime":dateTime , "section":article['section_name'] , "subsection":subsection_name , 
                        "headline":article['abstract'] , "description":article['lead_paragraph'] , "location":location , 
                        "webURL":article['web_url'] , "imageURL":imageURL})
                    
                    else:
                        myArticleManyLocations.append({"datetime":dateTime , "section":article['section_name'] , "subsection":subsection_name , 
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

        mycol1.insert_many(myArticleNoLocation)
        mycol2.insert_many(myArticleOneLocation)
        mycol3.insert_many(myArticleManyLocations)


            



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