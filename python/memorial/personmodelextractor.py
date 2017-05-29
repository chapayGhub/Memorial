import json
import urllib3
from bs4 import BeautifulSoup
import os
import codecs
import genson

#create json schema from raw json data
class PersonModelExtractor:
    def __init__(self):
        self._schema = genson.Schema()

    def extractFrom(self, dir):
        if os.path.exists(dir):
            dataFiles = os.listdir(dir)
            itemsCount = len(dataFiles)
            index = 0

            for dataFilename in dataFiles:
                print ("data file : ({0})({1}/{2}): {3}".format(index / itemsCount, index, itemsCount, dataFilename))
                index += 1
                file = "{0}/{1}".format(dir, dataFilename)
                if os.path.isfile(file ):
                    fobj = codecs.open(file , "r", "utf-8")
                    data = json.load(fobj)
                    fobj.close()
                    for item in data:
                        self.extract(item)

    def extract(self, json):
        self._schema.add_object(json)


    def schema(self):
        return self._schema