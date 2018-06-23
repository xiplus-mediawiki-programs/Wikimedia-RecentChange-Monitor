# -*- coding: utf-8 -*-
import os
import urllib.request
import json
import csv

os.chdir(os.path.dirname(os.path.abspath(__file__)))

url = "https://zh.wikipedia.org/w/api.php?action=query&list=abusefilters&abfprop=id%7Cdescription&abflimit=max&format=json"
res = urllib.request.urlopen(url).read().decode("utf8")
res = json.loads(res)
with open("abusefilter_list.csv", "w") as f:
    writer = csv.writer(f, delimiter=',', quotechar='"')
    for row in res["query"]["abusefilters"]:
        writer.writerow([row["id"], row["description"]])
