#!/usr/local/bin/python3
__author__ = 'andreipachtarou'

import json
import sys
import urllib3
from bs4 import BeautifulSoup
import os
import codecs

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

#parse "name" into fio
#parse "cont" field
#version 1.0
#   "name" split by space and assign secondname = name[0] firstname = name[1] patronymic = name[2]
class DataFormater:
    def __init__(self):
        self.version = 1.0
        self.data = []
        self.url = ""
        self.dir = None
        self.filename = ""
        self.in_filename = ""
        self.out_filename = ""

    def updateFilename(self):
        self.out_filename = self.filename[0:len(self.filename)-len(".json")]
        self.out_filename = "{0}_[{1}].json".format(self.out_filename, self.version)
        if self.dir:
            self.out_filename = "{0}/{1}".format(self.dir, self.out_filename)
            self.in_filename = "{0}/{1}".format(self.dir, self.filename)

    def setDir(self, dir):
        self.dir = dir
        self.updateFilename()

    def formate(self, filename):
        self._resetWithFilename(filename)
        self.data = []
        self.formateData()

    def isFormarted(self, filename):
        self._resetWithFilename(filename)
        return os.path.isfile(self.out_filename)

    def _resetWithFilename(self, filename):
        if filename == self.filename:
            return
        self.filename = filename
        self.updateFilename()

    def formateData(self):
        inData = []
        if os.path.isfile(self.in_filename):
            fobj = codecs.open(self.in_filename, "r", "utf-8")
            inData = json.load(fobj)
            fobj.close()
            for item in inData:
                parsedItem = {}
                parsedItem["fsp"] = {}
                self.extractSourceInformation(item["author"],parsedItem)
                self.extractFIO(item["name"], parsedItem)
                self.parseContent(item["cont"], parsedItem)

                self.data.append(parsedItem)

    def extractSourceInformation(self, source, parsed):
        markers = ["Источник:"]
        for marker in markers:
            pos = source.find(marker)
            if pos>=0:
                parsed["source"] = source[pos+len(marker):].strip()
                return True
        parsed["source"] = source
        return False

    def extractFIO(self, fio, parsed):
        fsp = parsed["fsp"]
        fioList = list(filter(None, fio.split(" ")))
        if len(fioList) >= 3:
            fsp["firstname"] = fioList[1]
            fsp["secondname"] = fioList[0]
            fsp["patronymic"] = fioList[2]
        elif len(fioList) == 2:
            fsp["firstname"] = fioList[1]
            fsp["secondname"] = fioList[0]
        elif len(fioList) == 1:
            fsp["firstname"] = fioList[0]

        if len(fioList) >= 4:
            fsp["nameparts"] = " ".join(fioList[3:])
            print("{0}->{1}:\nname:{2}".format(self.in_filename, self.out_filename, fio))

    def parseContent(self, content, parsed):
        contentList = list(content.split("\n"))
        methods = [
                    "extractBornInformation",
                    "extractShotInformation",
                    "extractArrestedInformation",
                    "extractRehabilitatedInformation",
                    "extractVerdictMakertInformation",
                    "extractVerdictInformation",
                    "extractLocationInformation",
                    "extractPatronimicVariantsInformation",
                    "extractFirstnameVariantsInformation",
                    "extractFspVariantsInformation"];
        index = 0
        for contentItem in contentList:
            processed = False
            if len(contentItem):
                for method in methods:
                    if getattr(self, method)(contentItem, parsed, index)==True:
                        processed = True
                        break
                if processed==False:
                    self.extractUnparsedInformation(contentItem, parsed, index)
            index = index+1

    def extractUnparsedInformation(self, contentItem, parsed, index):
        if index == 2:
            parsed["job"] = contentItem
        else:
            parsed["unparsed_{0}".format(index)] = contentItem

    def extractFspVariantsInformation(self, contentItem, parsed, index):
        markers = ["варианты ФИО"]
        for marker in markers:
            pos = contentItem.find(marker)
            if pos >= 0:
                fsp= contentItem[pos+len(marker):].strip(' ():')
                parsed["fsp"]["fsp_variants"] = fsp
                return True
        return False

    def extractFirstnameVariantsInformation(self, contentItem, parsed, index):
        markers = ["варианты имени"]
        for marker in markers:
            pos = contentItem.find(marker)
            if pos >= 0:
                firstname= contentItem[pos+len(marker):].strip(' ():')
                parsed["fsp"]["firstname_variants"] = firstname
                return True
        return False

    def extractPatronimicVariantsInformation(self, contentItem, parsed, index):
        markers = ["варианты отчества"]
        for marker in markers:
            pos = contentItem.find(marker)
            if pos >= 0:
                patronymic = contentItem[pos+len(marker):].strip(' ():')
                parsed["fsp"]["patronymic_variants"] = patronymic
                return True
        return False

    def extractShotInformation(self, contentItem, parsed, index):
        markers = ["Расстреляна", "Расстрелян"]
        for marker in markers:
            pos = contentItem.find(marker)
            if pos>=0:
                parsed["shot"] = contentItem[pos+len(marker):].strip()
                return True
        return False

    def extractArrestedInformation(self, contentItem, parsed, index):
        markers = ["Арестован", "Арестована"]
        for marker in markers:
            pos = contentItem.find(marker)
            if pos>=0:
                parsed["arrested"] = contentItem[pos+len(marker):].strip()
                return True
        return False

    def extractRehabilitatedInformation(self, contentItem, parsed, index):
        markers = ["Реабилитирована", "Реабилитирован"]
        for marker in markers:
            pos = contentItem.find(marker)
            if pos>=0:
                parsed["rehabilitated"] = contentItem[pos+len(marker):].strip()
                return True
        return False

    def extractBornInformation(self, contentItem, parsed, index):
        markers = ["Родилась", "Родился"]
        for marker in markers:
            pos = contentItem.find(marker)
            if pos>=0:
                parsed["born"] = contentItem[pos+len(marker):].strip()
                return True
        return False

    def extractVerdictMakertInformation(self, contentItem, parsed, index):
        markers = ["Приговорена:","Приговорен:"]
        for marker in markers:
            pos = contentItem.find(marker)
            if pos>=0:
                parsed["verdictmaker"] = contentItem[pos+len(marker):].strip()
                return True
        return False

    def extractVerdictInformation(self, contentItem, parsed, index):
        markers = ["Приговор:"]
        for marker in markers:
            pos = contentItem.find(marker)
            if pos>=0:
                parsed["verdict"] = contentItem[pos+len(marker):].strip()
                return True
        return False

    def extractLocationInformation(self, contentItem, parsed, index):
        markers = ["Проживала:", "Проживал:"]
        for marker in markers:
            pos = contentItem.find(marker)
            if pos>=0:
                parsed["location"] = contentItem[pos+len(marker):].strip()
                return True
        return False

    def save(self):
        fobj = codecs.open(self.out_filename, "w", "utf-8")
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