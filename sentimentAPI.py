from flask import Flask, request, Response, jsonify
import  requests
import json
import jsonpickle
import logging
import codecs

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


# Initialize the Flask application
app = Flask(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.DEBUG)


def getSentiment(sentence):
    sid_obj = SentimentIntensityAnalyzer()
    sentiment_dict = sid_obj.polarity_scores(sentence)
    sentimentScore = sentiment_dict['compound']
    return sentimentScore


@app.route('/apiv1/sentiment', methods=[ 'GET'])
def sentiment():
    sentences = json.loads(request.data)
    print(sentences)
    sentences = list(sentences)
    response = []

    try:
        for sentence in sentences:
            score = getSentiment(sentence)
            response.append(score) 
    
    except:
        print("Request to sentiment endpoint was unsuccessful.")

    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")

app.run(host="0.0.0.0", port=5000)