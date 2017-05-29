#!/usr/local/bin/python3
__author__ = 'andreipachtarou'

import json
import sys
import urllib3
from bs4 import BeautifulSoup
import os
import codecs
from personmodelextractor import PersonModelExtractor

def jdefault(o):
    return o.__dict__

# targetDir = "./etalon"
targetDir = "./data"

if __name__ == '__main__':

    def main(args):
        modelExtractor = PersonModelExtractor()
        modelExtractor.extractFrom(targetDir)
        print (modelExtractor.schema())

    main(sys.argv[1:])

# url = "http://lists.memo.ru/d1/f1.htm"