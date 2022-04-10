db.createView("articleNoImageThumb", "article", [{$match: {"imageURL" : {$exists: false}}}])
db.article.deleteMany({})
db.location.deleteMany({})
db.article.distinct("locationsRaw")