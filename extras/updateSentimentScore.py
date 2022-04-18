
import os, sys, inspect, json
from bson import ObjectId
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

import mongodb
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def getSentiment(sentence):
    sid_obj = SentimentIntensityAnalyzer()
    sentiment_dict = sid_obj.polarity_scores(sentence)
    sentimentScore = sentiment_dict['compound']
    return sentimentScore

client = mongodb.dbConnection()
mydb = mongodb.createdb(client)
articleCollection = mydb["article"]
apiErrorCollection = mydb["api_error"]
class MongoDbEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat() + 'Z'
        if isinstance(obj, ObjectId):
            return str(obj)
        return json.JSONEncoder.default(self, obj)

# startYear = CONSTANTS["START_YEAR"]
# endYear = CONSTANTS["END_YEAR"]
# stepYear = CONSTANTS["STEP_YEAR"]
# startMonth = CONSTANTS["START_MONTH"]
# endMonth = CONSTANTS["END_MONTH"]

startYear = 2021
endYear = 2021
stepYear = 1
startMonth = 2
endMonth = 2

def processSequentially(articlesList):
    articlesListWithSentiment = []
    for article in articlesList:
        text = article['headline'] + '- ' + article['abstract']
        article['sentimentScore'] = getSentiment(text)
        articlesListWithSentiment.append(article)
    print(len(articlesList))
    return articlesListWithSentiment

def processParallely(articlesList):
    articlesListWithSentiment = []
    print(len(articlesList))
    return articlesListWithSentiment

try:
    for year in range(startYear, endYear + stepYear, stepYear):
        print(f"Year: {year}")
        for month in range(startMonth, endMonth + 1):
            print(f"Month: {month}")
            articlesList = None
            with open(f'sample/{year}-{month}.json', 'r', encoding='utf-8') as f:
                articlesList = json.load(f)

            # startDate = datetime(int(year), int(month), 1)
            # endDate = startDate + relativedelta(months=+1)
            # print(startDate, endDate)
            # query = { "sentimentScore": {"$exists" : False}, "dateTime": { "$gte": startDate, "$lt": endDate } }
            # articles = articleCollection.find(query, { '_id': 1, 'headline': 1, 'abstract': 1 })
            # articlesList = list(articles)
            # # print(len(articlesList))
            # with open(f'sample/{year}-{month}.json', 'w', encoding='utf-8') as f:
            #     json.dump(articlesList, f, indent=2, cls=MongoDbEncoder)

            startTime = datetime.now()
            articlesListWithSentiment = processSequentially(articlesList)
            endTime = datetime.now()
            print(f"Total execution time: {endTime-startTime}")
            
            with open(f'sample/{year}-{month}-op.json', 'w', encoding='utf-8') as f:
                json.dump(articlesListWithSentiment, f, indent=2, cls=MongoDbEncoder)

            # # Create a list with object id and abstract field, use abstract field to pass it sentiment analyser
            # bulk = articleCollection.initialize_unordered_bulk_op()
            # counter = 0
            # for a in articlesList:
            #     a['sentimentScore'] = getSentiment(a['abstract'])
            # print(articlesList)

            # for a in articlesList:
            #     # process in bulk
            #     bulk.find({ '_id': a['_id'] }).update({ '$set': { 'sentimentScore': a['sentimentScore']} })
            #     counter += 1

            #     if (counter % 500 == 0):
            #         bulk.execute()
            #         bulk = articleCollection.initialize_ordered_bulk_op()

            #     if (counter % 500 != 0):
            #         bulk.execute()

            # articles = articleCollection.find(query, {'_id':1,'abstract':1}).limit(30)
            # articlesList = list(articles)
            # print(articlesList)
            
except:
    errorInfo = sys.exc_info()
    print(errorInfo)
    # error = str(errorInfo[0])
    # if error != "<class 'KeyboardInterrupt'>":
    #     exceptionData = {"year": year, "month": month, "dateTime": datetime.now(), "error": error}
    #     print("Exception data", exceptionData)
    #     apiErrorCollection.insert_one(exceptionData)
    