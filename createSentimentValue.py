import mongodb
import sys
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import jsonpickle

def getSentiment(sentence):
    sid_obj = SentimentIntensityAnalyzer()
    sentiment_dict = sid_obj.polarity_scores(sentence)
    sentimentScore = sentiment_dict['compound']
    return sentimentScore

client = mongodb.dbConnection()
mydb = mongodb.createdb(client)
articleCollection = mydb["article"]
apiErrorCollection = mydb["api_error"]

# startYear = CONSTANTS["START_YEAR"]
# endYear = CONSTANTS["END_YEAR"]
# stepYear = CONSTANTS["STEP_YEAR"]
# startMonth = CONSTANTS["START_MONTH"]
# endMonth = CONSTANTS["END_MONTH"]

startYear = 2018
endYear = 2019
stepYear = 1
startMonth = 1
endMonth = 12

try:
    for year in range(startYear, endYear + stepYear, stepYear):
        print(f"Year: {year}")
        for month in range(startMonth, endMonth + 1):
            startDate = datetime(int(year), int(month), 1)
            # endDate = startDate.AddMonths(1).AddDays(-1)
            endDate = startDate + relativedelta(day=31)
            # print(startDate)
            # print(endDate)
            query = { "dateTime": { "$gte": startDate, "$lt": endDate } }
            articles = articleCollection.find(query, {'_id':1,'abstract':1})
            articlesList = list(articles)
            print(articlesList)

            # Create a list with object id and abstract field, use abstract field to pass it sentiment analyser
            bulk = articleCollection.initialize_unordered_bulk_op()
            counter = 0
            for a in articlesList:
                a['sentimentScore'] = getSentiment(a['abstract'])
            print(articlesList)

            for a in articlesList:
                # process in bulk
                bulk.find({ '_id': a['_id'] }).update({ '$set': { 'sentimentScore': a['sentimentScore']} })
                counter += 1

                if (counter % 500 == 0):
                    bulk.execute()
                    bulk = articleCollection.initialize_ordered_bulk_op()

                if (counter % 500 != 0):
                    bulk.execute()

            articles = articleCollection.find(query, {'_id':1,'abstract':1}).limit(30)
            articlesList = list(articles)
            print(articlesList)
            
except:
    errorInfo = sys.exc_info()
    print(errorInfo)
    # error = str(errorInfo[0])
    # if error != "<class 'KeyboardInterrupt'>":
    #     exceptionData = {"year": year, "month": month, "dateTime": datetime.now(), "error": error}
    #     print("Exception data", exceptionData)
    #     apiErrorCollection.insert_one(exceptionData)
    