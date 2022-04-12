db.article.find({ "imageURL": { $exists: false } })
db.createView("articleNoImageThumb", "article", [{ $match: { "imageURL": { $exists: false } } }])
db.article.deleteMany({})
db.article_raw.deleteMany({})
db.location.deleteMany({})
db.article.distinct("locationsRaw").length
db.article.find({ dateTime: { $lt: new ISODate('2001:01:01') } })
db.article.updateMany({ "images": { $exists: true } }, { "$unset": { images: "" } })

db.article.aggregate([
    {
        "$project": {
            "year": { "$year": "$dateTime" },
        }
    },
    {
        "$group": {
            "_id": null,
            "distinctDate": { "$addToSet": { "year": "$year" } }
        }
    },
    { "$unwind": "$distinctDate" },
    { "$sort": { "distinctDate.year": 1 } }
])

db.article.aggregate(
    [
        {
            $group:
            {
                _id: {
                    $dateToString: {
                        "date": "$dateTime",
                        "format": "%Y-%m-%d"
                    }
                },
                count: { $sum: 1 }
            }
        },
        {
            $group:
            {
                "_id": "_id",
                AverageValue: { $avg: "$count" }
            }
        }
    ])

db.article.find().sort({ "dateTime": 1 }).limit(1)


db.article.aggregate([
    { $project: { "locationsRaw": 1 } },
    { $unwind: "$locationsRaw" },
    { $group: { _id: null, locations: { $addToSet: "$locationsRaw" } } },
    { $unwind: "$locations" },
    { $project: { _id: 0 } },
    { $group: { _id: null, count: { $sum: 1 } } },
])


db.article.aggregate([
    { $project: { "locationsRaw": 1 } },
    { $unwind: "$locationsRaw" },
    { $group: { _id: null, location: { $addToSet: "$locationsRaw" } } },
    { $unwind: "$location" },
    { $project: { _id: 0 } },
    { $out: "location" }
])

db.location.updateMany({}, { $rename: { 'locations': 'location' } })

let batch = [];
db.article.find({}).forEach(
    function (doc) {
        batch.push({
            "updateOne": {
                "filter": { "_id": doc._id },
                "update": { "$set": { "locationsRawTrimmed": doc.locationsRaw.map(e => e.trim().replace(/\s+/g, ' ')) } }
            }
        });

        if (batch.length % 1000 == 0) {
            db.article.bulkWrite(batch);
            batch = [];
        }
    }
);
if (batch.length > 0) {
    db.article.bulkWrite(batch);
    batch = [];
}

db.article.find({ "locationsRawTrimmed": { $exists: false } })
db.article.updateMany({}, { "$unset": { locationsRaw: "" } });

db.article.aggregate([
    {
        $match: { uri: 'nyt://article/f9171427-eed3-5031-88fa-f3ba050a5cf3' }
    }
]);

db.article.aggregate([
    {
        $match: { uri: 'nyt://article/f9171427-eed3-5031-88fa-f3ba050a5cf3' }
    },
    {
        $lookup:
        {
            from: "location",
            localField: "locationsRawTrimmed",
            foreignField: "location",
            as: "locations"
        }
    },
    { $project: { _id: 0, locationsRawTrimmed: 0, "locations._id": 0 } },
    { $out: "article_loc" }
]);

db.article.aggregate([
    {
        $lookup:
        {
            from: "location",
            localField: "locationsRawTrimmed",
            foreignField: "location",
            as: "locations"
        }
    },
    { $project: { _id: 0, locationsRawTrimmed: 0, "locations._id": 0 } },
    { $out: "article_loc" }
]);

db.article.drop();
db.article_raw.drop();
db.article_loc.renameCollection('article');
