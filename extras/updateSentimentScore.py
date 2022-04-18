
import os, sys, inspect, json
from bson import ObjectId
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

import mongodb
from pymongo import InsertOne, DeleteMany, ReplaceOne, UpdateOne
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
sid_obj = SentimentIntensityAnalyzer()

import multiprocessing as mp
num_proc = mp.cpu_count()
print("Number of processors: ", num_proc)

def getSentiment(sentence):
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
startMonth = 1
endMonth = 1

def processSingle(article):
    text = article['headline'] + '- ' + article['abstract']
    article['sentimentScore'] = getSentiment(text)
    return article

def processSequentially(articlesList):
    for article in articlesList:
        processSingle(article)

def processParallely(articlesList):
    pool = mp.Pool(num_proc)
    return [pool.apply(processSingle, args=(article, )) for article in articlesList]

try:
    for year in range(startYear, endYear + stepYear, stepYear):
        print(f"Year: {year}")
        for month in range(startMonth, endMonth + 1):
            print(f"Month: {month}")

            # articlesList = None
            # with open(f'sample/{year}-{month}.json', 'r', encoding='utf-8') as f:
            #     articlesList = json.load(f)

            startDate = datetime(int(year), int(month), 1)
            endDate = startDate + relativedelta(months=+1)
            print(startDate, endDate)
            query = { "sentimentScore": {"$exists" : False}, "dateTime": { "$gte": startDate, "$lt": endDate } }
            articles = articleCollection.find(query, { '_id': 1, 'headline': 1, 'abstract': 1 })
            articlesList = list(articles)
            print(len(articlesList))

            # with open(f'sample/{year}-{month}.json', 'w', encoding='utf-8') as f:
            #     json.dump(articlesList, f, indent=2, cls=MongoDbEncoder)

            startTime = datetime.now()
            processSequentially(articlesList)
            # articlesList = processParallely(articlesList)
            endTime = datetime.now()
            print(f"Sentiment Score Calculation- Total execution time: {endTime-startTime}")
            
            # with open(f'sample/{year}-{month}-op.json', 'w', encoding='utf-8') as f:
            #     json.dump(articlesList, f, indent=2, cls=MongoDbEncoder)

            startTime = datetime.now()
            # Create a list with object id and abstract field, use abstract field to pass it sentiment analyser
            operations = []
            batchCount = 1

            for article in articlesList:
                operation = UpdateOne({'_id': article['_id']}, {'$set': {'sentimentScore': article['sentimentScore']}})
                operations.append(operation)

                if (len(operations) % 500 == 0):
                    print(f'Writing batch {batchCount}')
                    articleCollection.bulk_write(operations)
                    operations = []
                    batchCount += 1

            if (len(operations) > 0):
                print(f'Writing batch {batchCount}')
                articleCollection.bulk_write(operations)

            endTime = datetime.now()
            print(f"DB Bulk Write- Total execution time: {endTime-startTime}")
            
except Exception as e:
    raise e
    errorInfo = sys.exc_info()
    print(errorInfo)
    # error = str(errorInfo[0])
    # if error != "<class 'KeyboardInterrupt'>":
    #     exceptionData = {"year": year, "month": month, "dateTime": datetime.now(), "error": error}
    #     print("Exception data", exceptionData)
    #     apiErrorCollection.insert_one(exceptionData)
    