"nytimes"

from asyncio.windows_events import NULL
from pynytimes import NYTAPI
import datetime

myKey = ""
#outputFile = "C:\Users\Shiva\Desktop\Anu\UC BOULDERS\Courses\Spring 2022\ATLS 5214_Big Data Architecture\Project\output.txt"
nyt = NYTAPI(myKey, parse_dates=True)

"""
class Article:
    def __init__(self, dateTime, section, subsection, headline, description, location, webURL, imageURL):
        self.dateTime = dateTime
        self.section = section
        self.subsection = subsection
        self.headline = headline
        self.description = description
        self.locatuon = location
        self.webURL = webURL
        self.imageURL = imageURL
"""

def getData(year, month):
    data = nyt.archive_metadata(
    date = datetime.datetime(year, month, 1))
    nyt.close()
    return data


myArticle = []
for year in range(1850, 2022, -1):
    myArticle.clear()
    for month in range(1, 13, 1):
        articles = getData(year, month)
        for article in articles:
            if "subsection_name" in article.keys():
                subsection_name = article['subsection_name']
            else:
                subsection_name = "null"

            if "multimedia" in article.keys() and len(article['multimedia']) > 0:
                    imageURL = article['multimedia'][0]['url']
            else:
                imageURL = "null"

            for keyword in article["keywords"]:
                if keyword["name"] == "glocations":
                    location = keyword["value"]
                    elements = {"datetime":article["pub_date"] , "section":article['section_name'] , "subsection":subsection_name , 
                    "headline":article['abstract'] , "description":article['lead_paragraph'] , "location":location , 
                    "webURL":article['web_url'] , "imageURL":imageURL}
                    myArticle.append(str(elements))

print(myArticle[0])
          
#print(len(data))
#file1 = open(r"C:\Users\Shiva\Desktop\Anu\UC BOULDERS\Courses\Spring 2022\ATLS 5214_Big Data Architecture\Project\output.txt","w+", encoding="utf-8")
#file1.write(str(data))

#print (data)
#file1.close()
