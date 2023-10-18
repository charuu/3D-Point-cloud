import os
from flask import Flask, render_template, abort, url_for
import json
import html
from json2html import *
from json2table import convert
import re 
from bs4 import BeautifulSoup
app = Flask(__name__)

# read file
  
if __name__ == '__main__': 
    with open('../data.json', 'r') as myfile:
        data = json.load(myfile)

        d =json2html.convert(json = data)
        d = '<html>'+d+'</html>'
      
        soup = BeautifulSoup(d, "html.parser")

        text = soup.find_all("td")

        for t in text:
            if re.search(r'(?:/[^/]+)+?/*\w/.+\.jpg',t.get_text()):
                replacement = soup.new_tag('img', src=t.get_text(),width="300",height="150")
                t.clear()
                t.append(replacement)
                
            if re.search(r'(?:/[^/]+)+?/*\w/.+\.png',t.get_text()):
                replacement = soup.new_tag('img', src=t.get_text(),width="300",height="150")
                t.clear()
                t.append(replacement)


        html = soup.prettify("utf-8")        
        with open("output.html", "wb") as ht:
            print(html)
            ht.write(html)
        
    

    
                
                
                
                
                