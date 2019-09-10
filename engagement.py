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

# function to remove punctuation from the titles to get better assessment of keywords ' e.g. "Newest", == Newest
def punctuationremove(s):
    return s.translate(str.maketrans('', '', string.punctuation))

# Utilized for converting facebook like format to numerical value 'e.g., 1.8K -> 1800 , 1M -> 1000000
def numberFormatter(number2format):
    units={"K": 1000, "M": 1000000}
    try:
        return int(number2format)
    except ValueError:
        # find unit
        unit=number2format[-1]
        n=float(number2format[:-1])
        return int(n*units[unit])


# Removing the <loc> tags from the xml scraped data and converting from bytes-like to str
def pathfinder(tag):
    tree = ET.fromstring(str(tag))
    notags = (ET.tostring(tree, method='text')).decode('utf-8')

    return notags


# def getEngagement(url, token):
#     return graph.request(f'https://graph.facebook.com/v4.0/?id=https%3A%2F%2F{url}&fields=engagement&access_token={token}')
#
# token ='EAAfk1RqIFSkBAEbZA3tmqwdzfVJ0up3EQN2iADnnmtiaf2apgSiKZCEjmKZBDZAbcfRaH4Lz4QkMB3Qvrd6kPCq9GpPMEj26YC1kjYgL1zzZAqdWmHqsirNDvtWK7pa53C00RXKzbZAVPgRth7n02bkbqlrajq97ZBckyu9WADI79xdNM77BsEPcPSpJaZBRmhgZD'
# # url= 'www.boredpanda.com/unexpected-unusual-funny-cosplay-beebinch/'
# graph = facebook.GraphAPI(access_token=token, version = 3.1)


url = 'http://localhost:63342/CONTENTIQ/sitemapcopy.xml?_ijt=bj461fbak3vosnff3um6qrf5nc'


# Opening the csv file in for data input
# If previously scraped change second argument to 'a' to append, otherwise 'w' will overwrite existing data
# Analyze data prior to setting delimiter, for this use case comma-delimiting was not suitable
with open('engagementdata.csv', 'a') as csvfile:
    filewriter = csv.writer(csvfile, delimiter='\t',quotechar='|', quoting=csv.QUOTE_MINIMAL)
    # filewriter.writerow(['ID','Url','Title,','Average Points','Facebook Shares','Category 1','Category 2'])



    # Gather Data from site xml and create object of all <loc> tags
    html =requests.get(url).text
    soup = BeautifulSoup(html,'lxml')
    url_titles = soup.findAll('loc')

    # remove all loc tags from each of the elements to extract only urls
    # Alternatively, can iterate through and call 'find().text' to extract
    for index, url in enumerate(url_titles):
        url_titles[index] = pathfinder(url)
    print(url_titles)


    # initialize dictionary for storage of keywords
    # e.g. {keyword : occurances}
    keywords={}

    idCount= 18368



    for i in url_titles:
        # Make a request for each url to parse various attributes
        response = requests.get(i, headers={'User-Agent': 'Mozilla/5.0'})
        html_soup = BeautifulSoup(response.text, 'html.parser')
        title = html_soup.find('h1', class_='post-title').text
        post_content = html_soup.find('div', class_='post-content')


        # Not all articles have category.
        # Requires exception handling for stability
        try:
            category= html_soup.find('div', class_ = 'categories-list in-post').find_all('a')
            cat = [tag.text for tag in category]
        except AttributeError:
            cat = [None, None]

        #standardize characters to avoid duplicate keys
        # iterate through each word and check against keyword bank.
        # Increment if seen otherwise add new key
        for word in punctuationremove(title).lower().split(' '):
            if word not in keywords:
                keywords[word] = 1
            else:
                keywords[word] += 1

        #Gather all the up/down point values for posts on page
        post_points=[]
        # iterate through tags and extract the number of points
        for data in html_soup.findAll('div', class_='points'):
            post_points.append(int(data.get('data-points')))
        # Take the average as metric of post rating
        avg_points=round(sum(post_points)/len(post_points),2)

        # extract path for input in fblink 'e.g. contentIQ-is-way-ahead-of-the-game
        titlepath=urlparse(i).path.replace('/','')
        # extract network location 'e.g. www.boredpanda.com
        netloc= urlparse(i).netloc.replace('/','')

        # Because facebook share is loaded in via an iframe, it can't be scraped
        # src url is scraped for sharing data
        fblink=f'https://www.facebook.com/v2.8/plugins/like.php?action=like&app_id=469101399768819&channel=https%3A%2F%2Fstaticxx.facebook.com%2Fconnect%2Fxd_arbiter.php%3Fversion%3D44%23cb%3Df1081f1f74b4568%26domain%3D{netloc}%26origin%3Dhttps%253A%252F%252F{netloc}%252Ff1c50729d1d0eac%26relation%3Dparent.parent&container_width=60&href=http%3A%2F%2F{netloc}%2F{titlepath}%2F&layout=box_count&locale=en_US&sdk=joey&share=true&show_faces=false'
        fbhtml =requests.get(fblink).text
        fbdata= BeautifulSoup(fbhtml, 'html.parser')
        fb_shares = numberFormatter(fbdata.find('div', class_='_5n6j _5n6l').text)
        print(idCount)
        print(i)
        print(cat)
        print(title)
        print(avg_points)
        print(fb_shares)


        # handling inconsistent catergory sizes. Max is 2, Min is 0
        if len(cat)>1:

            filewriter.writerow([idCount, i, title, avg_points, fb_shares, cat[0], cat[1]])
        else:
            filewriter.writerow([idCount, i, title, avg_points, fb_shares, cat[0], None])

        idCount+=1

    print(keywords)

    csv_columns = ['Word', 'Count']
    with open('keywords.csv', 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(csv_columns)
        for key, value in keywords.items():
            writer.writerow([key, value])