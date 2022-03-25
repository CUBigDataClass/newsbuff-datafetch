#! /usr/bin/env python3
import ast, json, os
from fileinput import filename

# configure constant variables
START_YEAR = 2016
YEARS_COUNT = 5
PER_MONTH = 20
JSON_FILENAME = "myArticleOneLocation.json"

# derived constants
MONTHS = list(range(1, 13))
MONTHS_COUNT = len(MONTHS)
PER_YEAR = PER_MONTH * MONTHS_COUNT
TOTAL = PER_YEAR * YEARS_COUNT

def main():
    with open(JSON_FILENAME, 'r', encoding='utf-8') as f:
        myArticleOneLocation = json.load(f)
        print(len(myArticleOneLocation))
        print(START_YEAR, YEARS_COUNT, PER_MONTH, PER_YEAR, TOTAL)
        rowsDict = {}
        for i, value in enumerate(myArticleOneLocation):
            if i == TOTAL:
                break
            currentYear = START_YEAR + i // PER_YEAR
            currentMonth = 1 + (i % PER_YEAR) // PER_MONTH
            currentArticle = 1 + (i % PER_YEAR) % PER_MONTH
            # print(i, currentYear, currentMonth, currentArticle)
            if currentYear not in rowsDict:
                rowsDict[currentYear] = {}
            if currentMonth not in rowsDict[currentYear]:
                rowsDict[currentYear][currentMonth] = []
            value['location'] = value['location'][0]
            rowsDict[currentYear][currentMonth].append(value)
            if currentArticle == PER_MONTH:
                filename = f'sample-responses/{currentYear}/{currentMonth}.json'
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                with open(filename, 'w', encoding='utf-8') as f:
                    response = { 'success': True, 'rows': rowsDict[currentYear][currentMonth] }
                    json.dump(response, f, indent=4)

if __name__ == "__main__":
    main()