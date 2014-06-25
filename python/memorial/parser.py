__author__ = 'andreipachtarou'

import json
import sys
import urllib3
from bs4 import BeautifulSoup
import os

def jdefault(o):
    return o.__dict__

class DataLinks:
    def __init__(self):
        self.allUrls = []
        self.rootUrl = ""
        self.http = urllib3.PoolManager()

    def start(self, startUrl):
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
        fobj = open("contentLinks.json", "w")
        json.dump(self.allUrls, fobj)
        fobj.close()


if __name__ == '__main__':

    def main(args):
        links = DataLinks()
        if links.load()==False:
            links.start("http://lists.memo.ru")
            links.save()

    main(sys.argv[1:])