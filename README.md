# News Buff- Backend

## Introduction
-----------------------------------------------
- News Buff is an interactive world map of global news
- Check out the project on https://newsbuff.ml

## Description
-----------------------------------------------

- News pins are populated on the map depending on the user inputs - date, section, location
- Each news article's location is geocoded and shown on the map  
- Sentiment analysis is done on each news article to calculate a sentiment score from -1 to 1
- User Authentication with like and bookmark features for personalization

## Installation
-----------------------------------------------
1. To clone the repository:
```
git clone https://github.com/CUBigDataClass/newsbuff-datafetch.git
```
2. Create a free NYTIMES API key at https://developer.nytimes.com/apis
3. Create a GCP account
  - Deploy mongodb instance and get mongodb connection string
  - Create a Geocoding API key using https://developers.google.com/maps/documentation/geocoding/get-api-key
4. Host MongoDB and RabbitMQ
5. Save your keys in .env and app.yaml

## Requirements
-----------------------------------------------
- To install the requirements, run:
```
pip install -r requirements.txt
```

## Deployment
-----------------------------------------------
- To deploy on local machine:
```
export FLASK_APP=main.py
flask run
```

- To deploy on Google App Engine
https://cloud.google.com/appengine/docs/standard/nodejs/create-app

## CICD

Connected to GitHub actions, autodeploys on the main branch

## License
-----------------------------------------------
Distributed under the MIT License. See LICENSE.txt for more information