import datetime
from bs4 import BeautifulSoup
import tweepy
import requests
import time
import random
import json
import os

def path(file: str):
    return os.path.join(os.path.dirname(__file__), file)

def getJson(file: str) -> dict:
    with open(path(file), "r") as f:
        return json.load(f) 

def setJson(file: str, dict: dict):
    with open(path(file), "w") as f:
        json.dump(dict, f, indent=4)

keys = getJson("keys.json")

consumerKey     = keys["consumerKey"]
consumerSecret  = keys["consumerSecret"]
accessToken     = keys["accessToken"]
accessSecret    = keys["accessSecret"]

auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
auth.set_access_token(accessToken, accessSecret)
api = tweepy.API(auth)

badGalleries    = ["/wiki/BIONICLEsector01:Archive_Gallery", "/wiki/Gallery:Movies_and_Animations"]
domain          = "https://biosector01.com"

def getHTML(url: str):
    return BeautifulSoup(requests.get(url).content, "html.parser")

def strSlice(string: str, start: int, end: int):
    return string[start: len(string) - end]

def randomFrom(array: list):
    return array[random.randrange(0, len(array))]

def getString(tag):
    string = ""
    for item in tag.descendants:
        if isinstance(item, str):
            string += item.replace("\n", "")
    return string

def randomFilePageLink():
    galleryAnchor = randomFrom(galleryAnchors)
    galleryLink = galleryAnchor.get("href")
    if galleryLink not in badGalleries:
        galleryPage = getHTML(domain + galleryLink)
        galleryBox = randomFrom(galleryPage.find_all("li", {"class": "gallerybox"}))

        imageAnchor = galleryBox.find_all("a", {"class": "image"})[0]
        filePageLink = imageAnchor.get("href")

        if filePageLink in done:
            date = done[filePageLink]
            delta = now - datetime.datetime(date[0], date[1], date[2], 0, 0)
            if delta.days < 100:
                print(filePageLink, "was posted less than 100 days ago")
                return randomFilePageLink()

        caption = getString(galleryBox.find_all("div", {"class": "gallerytext"})[0])
        return filePageLink, caption, galleryLink
    else:
        return randomFilePageLink()

while True:
    now = datetime.datetime.now()

    done = getJson("done.json")


    print("-- Post attempt at " + str(now) + " --")
    posted = False
    while not posted:
        try:       
            galleriesPage = getHTML("https://biosector01.com/wiki/Category:Galleries")
            galleryAnchors = galleriesPage.find_all("div", {"class": "mw-category"})[0].find_all("a")
    
    
            filePageLink, caption, galleryLink = randomFilePageLink()
            filePage = getHTML(domain + filePageLink)      

            imageTag = filePage.find_all("img")[6]

            if caption == None or caption == "":
                caption = strSlice(imageTag.get("alt"), 5, 4) 

            pageLinks = filePage.find_all("li", {"class": "mw-imagepage-linkstoimage-ns0"})

            if len(pageLinks) == 0:
                link = domain + galleryLink
            else:       
                link = domain + pageLinks[0].findChildren("a", recursive=False)[0].get("href")

            with open(path("bonkle.png"), "wb") as image:
                image.write(requests.get(domain + imageTag.get("src")).content)

            caption = caption + ", " + link + " #Bionicle"
            print(caption)

            #api.update_with_media("bonkle.png", caption)

            done[filePageLink] = [now.year, now.month, now.day]

            setJson("done.json", done)

            posted = True
            
            print("Posted", filePageLink, "\n")
            time.sleep(1770) #1800
            
        except Exception as e: 
            print("EXCEPTION OCCURED:", e)
