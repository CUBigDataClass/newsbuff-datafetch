#! /usr/bin/env python3
import ast, json

def main():
    with open("myArticleOneLocation.txt",'r') as f:
        myArticleOneLocation = ast.literal_eval(f.read())
        with open('myArticleOneLocation.json', 'w', encoding='utf-8') as f:
            json.dump(myArticleOneLocation, f)

if __name__ == "__main__":
    main()