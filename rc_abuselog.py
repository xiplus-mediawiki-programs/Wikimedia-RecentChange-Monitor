# -*- coding: utf-8 -*-
import pymysql
import configparser
import json
import os
import re
import requests
import pickle
import datetime
import dateutil.parser
import pytz
import traceback
import csv
from http.cookiejar import CookieJar
import importlib
import time
from Monitor import *


sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)) + "/action")

os.environ['TZ'] = 'UTC'

M = Monitor()

try:
    from rc_config import module_list_abuselog
    print("module_list", module_list_abuselog)
except ImportError as e:
    if str(e) == "No module named 'rc_config'":
        traceback.print_exc()
    elif str(e) == "cannot import name 'module_list'":
        traceback.print_exc()
    else:
        M.error(traceback.format_exc())
        raise e

if not isinstance(module_list_abuselog, list):
    M.error("module_list is not a list")
    exit("module_list is not a list\n")

modules = []
for module_name in module_list_abuselog:
    if not isinstance(module_name, str):
        M.error("module_name '{}' is not a str".format(str(module_name)))
        exit("module_name '{}' is not a str\n".format(str(module_name)))
    try:
        module = importlib.import_module(module_name)
        if not hasattr(module, "main") or not callable(module.main):
            message = ("modue '{}' does not contain main function"
                       .format(module_name))
            M.error(message)
            exit(message)
        modules.append(module.main)
    except ImportError as e:
        M.error(traceback.format_exc())
        raise e


# login to wikimedia

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


# get latest timestamp

M.cur.execute("""SELECT `timestamp` FROM `RC_log_abuselog`
                 ORDER BY `timestamp` DESC LIMIT 1""")
rows = M.cur.fetchall()
if len(rows) > 0:
    timestamp = rows[0][0] + 1
else:
    timestamp = 0


def int2tz(timestamp):
    return (datetime.datetime.fromtimestamp(timestamp, tz=pytz.utc)
            .isoformat().replace('+00:00', 'Z'))


def tz2int(timestamp):
    return int(dateutil.parser.parse(timestamp).timestamp())


timestamp = int2tz(timestamp)

while True:
    try:
        print(timestamp)

        params = {
            'action': 'query',
            'list': 'abuselog',
            'aflstart': timestamp,
            'aflprop': 'ids|user|title|action|result|timestamp|hidden|revid|filter',
            'afldir': 'newer',
            'afllimit': '500',
            'format': 'json'
        }
        res = session.get(M.wp_api, params=params).json()

        for log in res["query"]["abuselog"]:
            print(log)

            for module in modules:
                try:
                    module(log)
                except Exception as e:
                    traceback.print_exc()
                    M.error(traceback.format_exc())

        if len(res["query"]["abuselog"]) > 0:
            timestamp = res["query"]["abuselog"][-1]["timestamp"]
            timestamp = int2tz(tz2int(timestamp) + 1)

    except Exception as e:
        traceback.print_exc()
        M.error(traceback.format_exc())

    time.sleep(60)
