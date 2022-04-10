db.find({ "imageURL": { $exists: false } })
db.createView("articleNoImageThumb", "article", [{ $match: { "imageURL": { $exists: false } } }])
db.article.deleteMany({})
db.location.deleteMany({})
db.article.distinct("locationsRaw")
db.find({ dateTime: { $lt: new ISODate('2001:01:01') } })
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