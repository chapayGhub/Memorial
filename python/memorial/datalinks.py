import json
import urllib3
from bs4 import BeautifulSoup
import os
import codecs

# get all urls to all htmls with target data
# if url not parsed previously
# parse them and save to file
class DataLinks:
    def __init__(self):
        self.allUrls = []
        self.rootUrl = ""
        self.http = urllib3.PoolManager()

    def loadLinks(self, startUrl):
        self.rootUrl = startUrl
        r = self.http.request('GET', self.rootUrl)
        soup = BeautifulSoup(r.data, "html.parser")
        abc = soup.find_all("p", "alefbet")

        for link in abc[0].find_all('a'):
            subUrl = "{0}/{1}".format(self.rootUrl, link.get('href'))
            self.subCategory(subUrl)

    def subCategory(self, url):
        r = self.http.request('GET', url)
        soup = BeautifulSoup(r.data, "html.parser")
        dop = soup.find_all("p", "doppoisk")

        subLinks = []
        for link in dop[0].find_all('a'):
            subUrl = "{0}/{1}".format(self.rootUrl, link.get('href'))
            subLinks.append(subUrl)
            self.contentLinks(subUrl)

        return

    def contentLinks(self, url):
        r = self.http.request('GET', url)
        soup = BeautifulSoup(r.data, "html.parser")
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