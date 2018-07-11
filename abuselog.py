# -*- coding: utf-8 -*-
import pymysql
import configparser
import json
import os
import requests
import pickle
import datetime
import dateutil.parser
import pytz
import traceback
import csv
from http.cookiejar import CookieJar
from Monitor import Monitor
from abuselog_config import afwatchlist, afblacklist

os.chdir(os.path.dirname(os.path.abspath(__file__)))

os.environ['TZ'] = 'UTC'

M = Monitor()

abusefilter_list = {}
with open('abusefilter_list.csv') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        abusefilter_list[int(row[0])] = row[1]


session = requests.Session()

try:
    with open('cookie.txt', 'rb') as f:
        cookies = pickle.load(f)
        session.cookies = cookies
except Exception as e:
    print("parse cookie file fail")

print("checking is logged in")
params = {'action': 'query', 'assert': 'user', 'format': 'json'}
res = session.get(M.wp_api, params=params).json()
if "error" in res:
    print("fetching login token")
    params = {
        'action': 'query',
        'meta': 'tokens',
        'type': 'login',
        'format': 'json'
        }
    res = session.get(M.wp_api, params=params).json()
    logintoken = res["query"]["tokens"]["logintoken"]

    print("logging in")
    params = {
        'action': 'login',
        'lgname': M.wp_user,
        'lgpassword': M.wp_pass,
        'lgtoken': logintoken,
        'format': 'json'
        }
    res = session.post(M.wp_api, data=params).json()
    if res["login"]["result"] == "Success":
        print("login success")
    else:
        exit("log in fail")

else:
    print("logged in")

with open('cookie.txt', 'wb') as f:
    pickle.dump(session.cookies, f)

M.cur.execute("""SELECT `timestamp` FROM `RC_log_abuselog`
                 ORDER BY `timestamp` DESC LIMIT 1""")
timestamp = M.cur.fetchall()[0][0]
timestamp = (datetime.datetime.fromtimestamp(timestamp+1, tz=pytz.utc)
             .isoformat().replace('+00:00', 'Z'))
print(timestamp)

params = {
    'action': 'query',
    'list': 'abuselog',
    'aflend': timestamp,
    'aflprop': 'ids|user|title|action|result|timestamp|hidden|revid|filter',
    'afllimit': '500',
    'format': 'json'
    }
res = session.get(M.wp_api, params=params).json()

try:
    afwatchlistname = []
    for id in afwatchlist:
        afwatchlistname.append(abusefilter_list[id])
    afblacklistname = []
    for id in afblacklist:
        afblacklistname.append(abusefilter_list[id])

    for log in res["query"]["abuselog"]:
        print(log["filter"], log["timestamp"])

        message = (
            M.link_user(log["user"]) + '於' + M.link_page(log["title"]) +
            '觸發' + M.link_abusefilter(log["filter_id"]) + '：' +
            log["filter"] + '（' + M.link_abuselog(log["id"])
        )
        if "revid" in log and log["revid"] != "":
            message += "|" + M.link_diff(log["revid"])
        message += '）'

        rows = M.check_user_blacklist(log["user"])
        if len(rows) != 0:
            message += (
                "\n（黑名單：\u200b" + M.parse_wikicode(rows[0][0]) + "\u200b")
            if rows[0][2] != "" and rows[0][2] != log["user"]:
                message += "，\u200b" + rows[0][2] + "\u200b"
            message += '，'+M.formattimediff(rows[0][1])+"）"

        if (len(rows) != 0
                or log["filter"] in afwatchlistname
                or log["filter"] in afblacklistname):
            M.sendmessage(
                message,
                log["user"] + "|" + M.wiki,
                log["title"] + "|" + M.wiki
            )

        if log["filter"] in afblacklistname:
            reason = "觸發過濾器：" + log["filter"]
            rows = M.check_user_blacklist_with_reason(log["user"], reason)
            if len(rows) == 0:
                M.addblack_user(
                    log["user"],
                    str(int(dateutil.parser.parse(log["timestamp"])
                                    .timestamp())),
                    reason,
                    msgprefix="自動"
                )
        M.addRC_log_abuselog(log)

except Exception as e:
    traceback.print_exc()
    M.error(traceback.format_exc())
