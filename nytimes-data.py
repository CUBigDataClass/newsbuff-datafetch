
# import csv
import datetime
# import json, 
import re
import sys
from datetime import datetime

import requests
from pymongo import errors
from pynytimes import NYTAPI
# from sqlalchemy import false

import mongodb
# import NYTSampleResponse
# import emitlogsBackend
# rabbitMQChannel, rabbitMQ = emitlogsBackend.fetchConnection()

# emitlogsBackend.log_info("Your info message - sample run example - info", rabbitMQChannel)
# emitlogsBackend.log_debug("Your debug message - sample run - debug", rabbitMQChannel)
# emitlogsBackend.log_warning("Your warning message - sample run - warning", rabbitMQChannel)

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
sid_obj = SentimentIntensityAnalyzer()

import os
from os.path import join, dirname
from dotenv import load_dotenv
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

CONSTANTS = {
    "START_YEAR": 2022,
    "END_YEAR": 2022,
    "STEP_YEAR": -1,
    "START_MONTH": 4,
    "END_MONTH": 4
}

# Specify API key to fetch the data
google_api_key = os.environ.get('GOOGLE_API_KEY', None)
myKey = os.environ.get('NYT_API_KEY', None)
nyt = NYTAPI(myKey, parse_dates=True)
currentTime = datetime.now()

def getSentiment(sentence):
    sentiment_dict = sid_obj.polarity_scores(sentence)
    sentimentScore = sentiment_dict['compound']
    return sentimentScore

# Function definition to fetch the NY times Archive data for given month and year.
def getNYTData(year, month):
    data = nyt.archive_metadata(date=datetime(year, month, 1))
    nyt.close()
    return data


def extract_lat_long_via_location(location):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    endpoint = f"{base_url}?address={location}&key={google_api_key}"
    r = requests.get(endpoint)
    if r.status_code not in range(200, 299):
        return None
    try:
        '''
        This try block incase any of our inputs are invalid. This is done instead
        of actually writing out handlers for all kinds of responses.
        '''
        results = r.json()['results'][0]
        latitude = results['geometry']['location']['lat']
        longitude = results['geometry']['location']['lng']
        return latitude, longitude
    except:
        return None


def processLocations(locations, locationsDict, locationCollection, locationErrorCollection):
    locationsMappedList = []
    locationsInsertList = []
    for location in locations:
        if location in locationsDict:
            locationsMappedList.append(locationsDict[location])
            # print(f"{location} found in Memory.")
        else:
            coordinates = extract_lat_long_via_location(location)
            if coordinates is not None:
                locationObj = {
                    "location": location,
                    "latitude": coordinates[0],
                    "longitude": coordinates[1]
                }
                locationsInsertList.append(locationObj)
                locationsMappedList.append(locationObj)
                locationsDict[location] = locationObj
                print(f"{location} fetched and found.")
            else:
                print(f"{location} fetched and not found.")
                locationErrorCollection.insert_one({"location": location})

    if len(locationsInsertList) > 0:
        locationCollection.insert_many(locationsInsertList)
        print(f"Inserted {len(locationsInsertList)} new locations in DB.", locationsInsertList)

    return locationsMappedList


def processNYTResponseType1(response, locationsDict, locationCollection, locationErrorCollection):
    articlesObjects = []

    for article in response:
        articleLocationsSet = set()
        for keyword in article["keywords"]:
            if keyword["name"] == "glocations":
                keyword["value"] = re.compile(r"\s+").sub(" ", keyword["value"].strip())
                articleLocationsSet.add(keyword["value"])

        if (len(articleLocationsSet) == 0):
            continue
        articleLocations = list(articleLocationsSet)

        articleMappedLocations = processLocations(
            articleLocations, locationsDict, locationCollection, locationErrorCollection)
        if (len(articleMappedLocations) == 0):
            continue
        
        # print('articleMappedLocations', articleMappedLocations)
        articleObject = {}
        articleObject["uri"] = article["uri"]
        articleObject["dateTime"] = article["pub_date"]
        articleObject["section"] = article["section_name"]
        articleObject["headline"] = article["headline"]["main"]
        articleObject["abstract"] = article["abstract"]
        articleObject["webURL"] = article["web_url"]

        text = articleObject['headline'] + '- ' + articleObject['abstract']
        articleObject['sentimentScore'] = getSentiment(text)

        imageURL = None
        for image in article['multimedia']:
            currentImageURL = "https://www.nytimes.com/" + image['url']
            if image["subtype"] == "thumbLarge":
                imageURL = currentImageURL
                break
        if imageURL:
            articleObject["imageURL"] = imageURL

        articleObject["locations"] = articleMappedLocations
        # articleObject["locationsRaw"] = articleLocations

        articlesObjects.append(articleObject)

    return articlesObjects


def main():

    client = mongodb.dbConnection()
    mydb = mongodb.createdb(client)
    articleCollection = mydb["article"]
    # print(datetime.now(), articleCollection.count_documents({ "locationsRaw": { "$exists": True } }))
    # return
    locationCollection = mydb["location"]
    apiErrorCollection = mydb["api_error"]
    locationErrorCollection = mydb["location_error"]
    countOld = articleCollection.count_documents({})

    resultCursor = locationCollection.find()
    locationResults = list(resultCursor)
    # locationsDict = {}
    locationsDict = {x["location"]: {"location": x["location"], "latitude": x["latitude"], "longitude": x["longitude"]} for x in locationResults}
    print(f"Loaded {len(locationsDict)} locations from DB.")

    startYear = CONSTANTS["START_YEAR"]
    endYear = CONSTANTS["END_YEAR"]
    stepYear = CONSTANTS["STEP_YEAR"]
    startMonth = CONSTANTS["START_MONTH"]
    endMonth = CONSTANTS["END_MONTH"]

    startTime = datetime.now()
    # Looping to fetch the data repeatedly for specified period of time.
    for year in range(startYear, endYear + stepYear, stepYear):
        print(f"Year: {year}")

        for month in range(startMonth, endMonth + 1):
            print(f"Year: {year}, Month: {month}, Waiting for NYT response...")
            try:
                articlesResponse = getNYTData(year, month)
                # articlesResponse = articlesResponse[:10]
                # articlesResponse = NYTSampleResponse.response
                print(f"Year: {year}, Month: {month}, Received NYT response.")
                # print(articlesResponse)

                articlesObjects = processNYTResponseType1(
                    articlesResponse, locationsDict, locationCollection, locationErrorCollection)
                print(
                    f"Year: {year}, Month: {month}, Count: {len(articlesObjects)}")

                if len(articlesObjects) > 0:
                    try:
                        # inserts new documents even on error
                        articleCollection.insert_many(
                            articlesObjects, ordered=False)
                    except errors.BulkWriteError as e:
                        panic_list = list(
                            filter(lambda x: x['code'] != 11000, e.details['writeErrors']))
                        if len(panic_list) > 0:
                            # print(f"these are not duplicate errors {panic_list}")
                            raise e

            except:
                errorInfo = sys.exc_info()
                print(errorInfo)
                error = str(errorInfo[0])
                if error != "<class 'KeyboardInterrupt'>":
                    exceptionData = {"year": year, "month": month, "dateTime": datetime.now(), "error": error}
                    print("Exception data", exceptionData)
                    apiErrorCollection.insert_one(exceptionData)

    countNew = articleCollection.count_documents({})
    countAdded = countNew - countOld
    msg = f"Added {countAdded} new articles, new total: {countNew}"
    print(msg)
    # emitlogsBackend.log_info(msg, rabbitMQChannel)

    endTime = datetime.now()
    print(f"Total execution time: {endTime-startTime}")


if __name__ == "__main__":
    main()
