db.createView("articleNoImageThumb", "article", [{$match: {"imageURL" : {$exists: false}}}])
