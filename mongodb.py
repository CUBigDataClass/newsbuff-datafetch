import os
from os.path import dirname, join

import pymongo
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

DB_URL = os.environ.get('DB_URL', None)

def dbConnection():
    try:
        #DB entry
        # Replace the uri string with your MongoDB deployment's connection string.
        # set a 5-second connection timeout
        client = pymongo.MongoClient(DB_URL, serverSelectionTimeoutMS=5000)
        print("Connected to the DB server.")
        # print(client.server_info())
        return client

    except Exception as error:
        print("Unable to connect to the DB server.")
        raise error
        

def createdb(client):
    mydb = client["testdbnewsbuff"]
    return mydb
