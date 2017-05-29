#!/usr/local/bin/python3
__author__ = 'andreipachtarou'

import json
import sys
import urllib3
from bs4 import BeautifulSoup
import os
import codecs
from dataformater import DataFormater
from dataextractor import DataExtractor
from datalinks import DataLinks

def jdefault(o):
    return o.__dict__


# targetDir = "./etalon"
targetDir = "./data"

if __name__ == '__main__':

    def filterFormatedFiles(filename):
        return filename.startswith(DataFormater.FormatedFilePrefix())

    def main(args):

        links = DataLinks()
        if links.load()==False:
            links.loadLinks("http://lists.memo.ru")
            links.save()

        data = DataExtractor()
        data.setDir("./data")

        itemsCount = len(links.allUrls)
        index = 0

        for url in links.allUrls:
            print ("target url: ({0})({1}/{2}): {3}".format(index/itemsCount, index, itemsCount, url))
            index += 1
            if data.isExtracted(url):
                continue
            data.extract(url)
            data.save()

        data = DataFormater()
        data.setDir(targetDir)
        dirContent = list(filter(filterFormatedFiles, os.listdir(targetDir)))

        index = 0
        itemsCount = len(dirContent)

        for file in dirContent:
            print ("data file: ({0})({1}/{2}): {3}".format(index/itemsCount, index, itemsCount, file))
            index += 1
            if  os.path.isfile("{0}/{1}".format(targetDir, file))==False \
                or file.endswith("].json")==True \
                or file.endswith(".json")==False:
                    continue
            data.formate(file)
            data.save()

    main(sys.argv[1:])

# url = "http://lists.memo.ru/d1/f1.htm"