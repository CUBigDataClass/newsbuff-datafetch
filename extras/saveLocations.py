import mongodb, json

def main():
    client = mongodb.dbConnection()
    mydb = mongodb.createdb(client)
    locationCollection = mydb["location"]

    resultCursor = locationCollection.find()
    locationResults = [x["location"] for x in list(resultCursor)]
    # print(locationResults)
    
    print(f"Loaded {len(locationResults)} locations from DB.")
    json.dump(locationResults, open('locations.json', 'w'), indent=2)

if __name__ == "__main__":
    main()
