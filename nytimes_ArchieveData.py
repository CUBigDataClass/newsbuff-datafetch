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
        article = getData(year, month)
        for a in article:
            if "subsection_name" in a.keys():
                ssname = a['subsection_name']
            else:
                ssname = "Null"
            elements = {datetime:a["pub_date"] , "section":a['section_name'] , "subsection":ssname , "headline":a['abstract'] , 
            "description":a['lead_paragraph'] , "location": , "webURL":a['web_url'] , "imageURL": }
            myArticle.append(str(elements))
            




print("hello")
#print(len(data))
#file1 = open(r"C:\Users\Shiva\Desktop\Anu\UC BOULDERS\Courses\Spring 2022\ATLS 5214_Big Data Architecture\Project\output.txt","w+", encoding="utf-8")
#file1.write(str(data))

#print (data)
#file1.close()
