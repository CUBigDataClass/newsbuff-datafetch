import pymongo

import mongodbconfig


def dbConnection():
    try:
        #DB entry
        # Replace the uri string with your MongoDB deployment's connection string.
        # set a 5-second connection timeout
        client = pymongo.MongoClient(mongodbconfig.conn_str, serverSelectionTimeoutMS=5000)
        print(client.server_info())
        return client

    except Exception:
        print("Unable to connect to the server.")

def createdb(client):
    mydb = client["testdbnewsbuff"]
    return mydb

def createclusters(mydb):
    mycol1 = mydb["customers1"]
    mycol = mydb["customers2"]
    mycol = mydb["customers3"]
