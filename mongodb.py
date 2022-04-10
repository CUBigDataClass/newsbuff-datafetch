import pymongo
import sys
import env


def dbConnection():
    try:
        #DB entry
        # Replace the uri string with your MongoDB deployment's connection string.
        # set a 5-second connection timeout
        client = pymongo.MongoClient(env.conn_str, serverSelectionTimeoutMS=5000)
        print("Connected to the DB server.")
        # print(client.server_info())
        return client

    except Exception as error:
        print("Unable to connect to the DB server.")
        raise error
        

def createdb(client):
    mydb = client["testdbnewsbuff"]
    return mydb
