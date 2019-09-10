from bs4 import BeautifulSoup
import urllib3
import facebook
import urllib.request
from urllib.parse import urlparse
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
import csv
import requests
import string
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

categories = {}
with open('engagementdata1.csv', 'r') as csvfile:
    csvreader = csv.reader(csvfile, delimiter='\t')
    line= 0
    for row in csvreader:
        id = row[0]
        url = row[1]
        title = row[2]
        avgpoints = row[3]
        fbshares = row[4]
        category1 = row[5]
        category2 = row[6]
        if line == 0:
            print(f'Column names are {", ".join(row)}')
            line +=1
        else:
            print(f'{id} , {url} , {title} , {avgpoints} , {fbshares} , {category1} , {category2}')
            objectdetails = {'url':url, 'title':title , 'Average Points':avgpoints , 'Facebook Shares':fbshares }

            # if fbshares == '':
            #     fbshares = 0
            if category1 != '':
                try:
                    if category1 not in categories:

                        categories[category1] = int(fbshares)

                    else:
                        categories[category1] += int(fbshares)
                except ValueError:
                    errorrow= row

                try:
                    if category2 not in categories:

                        categories[category2] = int(fbshares)

                    else:
                        categories[category2] += int(fbshares)
                except ValueError:
                    errorrow = row

    print(categories)

