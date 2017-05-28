import json
import urllib3
from bs4 import BeautifulSoup
import os
import codecs

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
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)

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
        soup = BeautifulSoup(r.data, "html.parser")
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