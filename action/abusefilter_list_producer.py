# -*- coding: utf-8 -*-
import json
import urllib.request

url = ("https://zh.wikipedia.org/w/api.php"
       + "?action=query&list=abusefilters&abfprop=id%7Cdescription"
       + "&abflimit=max&format=json")
res = urllib.request.urlopen(url).read().decode("utf8")
res = json.loads(res)
abusefilter_list = {}

for row in res["query"]["abusefilters"]:
    abusefilter_list[row["id"]] = row["description"]
