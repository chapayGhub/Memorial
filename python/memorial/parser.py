#!/usr/local/bin/python3
__author__ = 'andreipachtarou'

import json
import sys
import urllib3
from bs4 import BeautifulSoup
import os
import codecs
from  dataformater import DataFormater

def jdefault(o):
    return o.__dict__

# get all urls to all htmls with target data
# if url not parsed previously
# parse their and save to file
class DataLinks:
    def __init__(self):
        self.allUrls = []
        self.rootUrl = ""
        self.http = urllib3.PoolManager()

    def loadLinks(self, startUrl):
        self.rootUrl = startUrl
        r = self.http.request('GET', self.rootUrl)
        soup = BeautifulSoup(r.data)
        abc = soup.find_all("p", "alefbet")

        for link in abc[0].find_all('a'):
            subUrl = "{0}/{1}".format(self.rootUrl, link.get('href'))
            self.subCategory(subUrl)

    def subCategory(self, url):
        r = self.http.request('GET', url)
        soup = BeautifulSoup(r.data)
        dop = soup.find_all("p", "doppoisk")

        subLinks = []
        for link in dop[0].find_all('a'):
            subUrl = "{0}/{1}".format(self.rootUrl, link.get('href'))
            subLinks.append(subUrl)
            self.contentLinks(subUrl)

        return

    def contentLinks(self, url):
        r = self.http.request('GET', url)
        soup = BeautifulSoup(r.data)
        dop = soup.find_all("ul", "left-list")

        for link in dop[0].find_all('a'):
            lnk = link.get('href')
            lnk = "{0}/{1}".format(self.rootUrl, lnk[:lnk.find('#')])
            if lnk in self.allUrls:
                continue
            else:
                self.allUrls.append(lnk)
        return

    def urls(self):
        return self.allUrls

    def load(self):
        if os.path.isfile("contentLinks.json"):
            fobj = open("contentLinks.json", "r")
            self.allUrls = json.load(fobj)
            fobj.close()
            return True
        else:
            return False

    def save(self):
        fobj = codecs.open("contentLinks.json", "w", "utf-8")
        json.dump(self.allUrls, fobj, ensure_ascii=False)
        fobj.close()

#touch all html with target data
#extact data to json and save with name dir_filename
class DataExtractor:
    def __init__(self):
        self.http = urllib3.PoolManager()
        self.data = []
        self.url = ""
        self.dir = None
        self.filename = ""

    def updateFilename(self):
        parts = self.url.split('/')
        if len(parts)<=2:
            return
        parts = parts[len(parts)-2:]
        self.filename = parts[0]+"_"+parts[1][parts[1].rfind('/')+1:parts[1].rfind('.')]+".json"
        if self.dir:
            self.filename = "{0}/{1}".format(self.dir, self.filename)

    def setDir(self, dir):
        self.dir = dir
        self.updateFilename()

    def extract(self, url):
        self.resetWithUrl(url)
        self.data = []
        self.parseData()

    def isExtracted(self, url):
        self.resetWithUrl(url)
        return os.path.isfile(self.filename)

    def resetWithUrl(self, url):
        if url == self.url:
            return
        self.url = url
        self.updateFilename()

    def parseData(self):
        r = self.http.request('GET', self.url)
        soup = BeautifulSoup(r.data)
        for item in soup.find_all("li"):
            parsedItem = {}
            parsedItem["name"] = item.find("p", "name").get_text()
            parsedItem["cont"] = item.find("p", "cont").get_text()
            parsedItem["author"] = item.find("p", "author").get_text()
            self.data.append(parsedItem)
        return

    def load(self):
        if os.path.isfile(self.filename):
            fobj = open(self.filename, "r")
            self.data = json.load(fobj)
            fobj.close()
            return True
        else:
            return False

    def save(self):
        fobj = codecs.open(self.filename, "w", "utf-8")
        json.dump(self.data, fobj, ensure_ascii=False)
        fobj.close()



if __name__ == '__main__':

    def main(args):

        # links = DataLinks()
        # if links.load()==False:
        #     links.loadLinks("http://lists.memo.ru")
        #     links.save()
        #
        # data = DataExtractor()
        # data.setDir("./data")
        # for url in links.allUrls:
        #     if data.isExtracted(url):
        #         continue
        #     data.extract(url)
        #     data.save()

        targetDir = "./etalon"
        data = DataFormater()
        data.setDir(targetDir)
        dirContent = os.listdir(targetDir)
        for file in dirContent:
            if  os.path.isfile("{0}/{1}".format(targetDir, file))==False \
                or file.endswith("].json")==True \
                or file.endswith(".json")==False:
                    continue
            data.formate(file)
            data.save()

    main(sys.argv[1:])

# url = "http://lists.memo.ru/d1/f1.htm"