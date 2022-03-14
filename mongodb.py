import pymongo
from urllib3 import Retry
import mongodbconfig


def dbConnection():
    try:
        #DB entry
        # Replace the uri string with your MongoDB deployment's connection string.
        conn_str = "mongodb+srv://newsbuff:"+mongodbconfig.mongoDBPwd+"@newbuffcluster.j94k7.mongodb.net/test?retryWrites=true&w=majority"
        # set a 5-second connection timeout
        client = pymongo.MongoClient(conn_str, serverSelectionTimeoutMS=5000)
        print(client.server_info())
        return client

    except Exception:
        print("Unable to connect to the server.")

def createdb(client):
    dblist = client.list_database_names()
    if "testdbnewsbuff" in dblist:
        print("The database exists.")
    else:
        mydb = client["testdbnewsbuff"]
    return mydb

def createclusters(mydb):
    mycol = mydb["customers1"]
    mycol = mydb["customers2"]
    mycol = mydb["customers3"]