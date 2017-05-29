import json
import sys
import urllib3
from bs4 import BeautifulSoup
import os
import codecs

import sqlite3

#parse "name" into fio
#parse "cont" field
#version 1.0
#   "name" split by space and assign secondname = name[0] firstname = name[1] patronymic = name[2]

class DataFormater:
    def __init__(self):
        self.version = DataFormater.Version()
        self.data = []
        self.url = ""
        self.dir = None
        self.filename = ""
        self.in_filename = ""
        self.out_filename = ""

    @staticmethod
    def Version():
        return 0.1

    @staticmethod
    def FormatedFilePrefix():
        return "[{0}]".format(DataFormater.Version())

    def updateFilename(self):
        self.out_filename = self.filename[0:len(self.filename)-len(".json")]
        self.out_filename = "[{0}]_{1}.json".format(self.version, self.out_filename)
        if self.dir:
            self.out_filename = "{0}/{1}".format(self.dir, self.out_filename)
            self.in_filename = "{0}/{1}".format(self.dir, self.filename)

    def setDir(self, dir):
        self.dir = dir
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)

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

                self.addExtracted(parsedItem)

    def addExtracted(self, parsedItem):
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
                    "extractSecondnameVariantsInformation",
                    "extractFspVariantsInformation",
                    "extractPlaceBurialInformation"];
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
            parsed["job"] = contentItem.strip(' -.,():')
        else:
            parsed["unparsed_{0}".format(index)] = contentItem

    def extractFspVariantsInformation(self, contentItem, parsed, index):
        markers = ["варианты ФИО"]
        for marker in markers:
            pos = contentItem.find(marker)
            if pos >= 0:
                fsp= contentItem[pos+len(marker):].strip(' -.,():')
                parsed["fsp"]["fsp_variants"] = fsp
                return True
        return False

    def extractSecondnameVariantsInformation(self, contentItem, parsed, index):
        markers = ["варианты фамилии"]
        for marker in markers:
            pos = contentItem.find(marker)
            if pos >= 0:
                fsp= contentItem[pos+len(marker):].strip(' -.,():')
                parsed["fsp"]["secondtname_variants"] = fsp
                return True
        return False

    def extractPlaceBurialInformation(self, contentItem, parsed, index):
        markers = ["Место захоронения"]
        for marker in markers:
            pos = contentItem.find(marker)
            if pos >= 0:
                parsed["placeburial"] = contentItem[pos+len(marker):].strip(' -.,():')
                return True
        return False

    def extractFirstnameVariantsInformation(self, contentItem, parsed, index):
        markers = ["варианты имени"]
        for marker in markers:
            pos = contentItem.find(marker)
            if pos >= 0:
                firstname= contentItem[pos+len(marker):].strip(' -.,():')
                parsed["fsp"]["firstname_variants"] = firstname
                return True
        return False

    def extractPatronimicVariantsInformation(self, contentItem, parsed, index):
        markers = ["варианты отчества"]
        for marker in markers:
            pos = contentItem.find(marker)
            if pos >= 0:
                patronymic = contentItem[pos+len(marker):].strip(' -.,():')
                parsed["fsp"]["patronymic_variants"] = patronymic
                return True
        return False

    def extractShotInformation(self, contentItem, parsed, index):
        markers = ["Расстреляна", "Расстрелян"]
        for marker in markers:
            pos = contentItem.find(marker)
            if pos>=0:
                parsed["shot"] = contentItem[pos+len(marker):].strip(' -.,():')
                return True
        return False

    def extractArrestedInformation(self, contentItem, parsed, index):
        markers = ["Арестован", "Арестована", "Арест."]
        for marker in markers:
            pos = contentItem.find(marker)
            if pos>=0:
                parsed["arrested"] = contentItem[pos+len(marker):].strip()
                return True
        return False

    def extractRehabilitatedInformation(self, contentItem, parsed, index):
        markers = ["Реабилитирована", "Реабилитирован", "Реабил."]
        for marker in markers:
            pos = contentItem.find(marker)
            if pos>=0:
                parsed["rehabilitated"] = contentItem[pos+len(marker):].strip(' -.,():')
                return True
        return False

    def extractBornInformation(self, contentItem, parsed, index):
        markers = ["Родилась", "Родился", "Род."]
        for marker in markers:
            pos = contentItem.find(marker)
            if pos>=0:
                parsed["born"] = contentItem[pos+len(marker):].strip(' -.,():')
                return True
        return False

    def extractVerdictMakertInformation(self, contentItem, parsed, index):
        markers = ["Приговорена:","Приговорен:"]
        for marker in markers:
            pos = contentItem.find(marker)
            if pos>=0:
                parsed["verdictmaker"] = contentItem[pos+len(marker):].strip(' -.,():')
                return True
        return False

    def extractVerdictInformation(self, contentItem, parsed, index):
        markers = ["Приговор:"]
        for marker in markers:
            pos = contentItem.find(marker)
            if pos>=0:
                parsed["verdict"] = contentItem[pos+len(marker):].strip(' -.,():')
                return True
        return False

    def extractLocationInformation(self, contentItem, parsed, index):
        markers = ["Проживала:", "Проживал:", "Прож."]
        for marker in markers:
            pos = contentItem.find(marker)
            if pos>=0:
                parsed["location"] = contentItem[pos+len(marker):].strip(' -.,():')
                return True
        return False

    def save(self):
        #
        # conn = sqlite3.connect('test.db')
        # print("Opened database successfully")
        # conn.execute('''CREATE TABLE COMPANY
        #        (ID INT PRIMARY KEY     NOT NULL,
        #        NAME           TEXT    NOT NULL,
        #        AGE            INT     NOT NULL,
        #        ADDRESS        CHAR(50),
        #        SALARY         REAL);''')
        # print("Table created successfully")
        # conn.close()
        fobj = codecs.open(self.out_filename, "w", "utf-8")
        json.dump(self.data, fobj, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': '))
        fobj.close()