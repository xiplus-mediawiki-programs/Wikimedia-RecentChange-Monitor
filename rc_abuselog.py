# -*- coding: utf-8 -*-
import datetime
import importlib
import logging
import os
import pickle
import sys
import time
import traceback

import dateutil.parser
import pytz

import requests
from action.abusefilter_list_producer import abusefilter_list_rev
from Monitor import Monitor

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)) + "/action")

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(filename)20s:%(lineno)4s] %(levelname)7s %(message)s')

os.environ['TZ'] = 'UTC'

M = Monitor()

try:
    from rc_config import module_list_abuselog
    logging.info("module_list {}".format(module_list_abuselog))
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
session.headers.update({'User-Agent': M.wp_user_agent})

try:
    with open('cookie.txt', 'rb') as f:
        cookies = pickle.load(f)
        session.cookies = cookies
except Exception as e:
    print("parse cookie file fail")

logging.info("checking is logged in")
params = {'action': 'query', 'assert': 'user', 'format': 'json'}
res = session.get(M.wp_api, params=params).json()
if "error" in res:
    logging.info("fetching login token")
    params = {
        'action': 'query',
        'meta': 'tokens',
        'type': 'login',
        'format': 'json'
    }
    res = session.get(M.wp_api, params=params).json()
    logintoken = res["query"]["tokens"]["logintoken"]

    logging.info("logging in as {}".format(M.wp_user))
    params = {
        'action': 'login',
        'lgname': M.wp_user,
        'lgpassword': M.wp_pass,
        'lgtoken': logintoken,
        'format': 'json'
    }
    res = session.post(M.wp_api, data=params).json()
    if res["login"]["result"] == "Success":
        logging.info("login success")
    else:
        exit("log in fail: {}".format(res))

else:
    logging.info("logged in")

with open('cookie.txt', 'wb') as f:
    pickle.dump(session.cookies, f)


def int2tz(timeint):
    return (datetime.datetime.fromtimestamp(timeint, tz=pytz.utc)
            .isoformat().replace('+00:00', 'Z'))


def tz2int(timetz):
    return int(dateutil.parser.parse(timetz).timestamp())


timestamp = int2tz(int(time.time()))

while True:
    try:
        logging.info('query {}'.format(timestamp))

        params = {
            'action': 'query',
            'list': 'abuselog',
            'aflstart': timestamp,
            'aflprop': 'ids|user|title|action|result|timestamp|hidden|revid|filter|details',
            'afldir': 'newer',
            'afllimit': '500',
            'format': 'json'
        }
        res = session.get(M.wp_api, params=params).json()

        for log in res["query"]["abuselog"]:
            if log['filter_id'] == '':
                log['filter_id'] = abusefilter_list_rev[log['filter']]
            log['filter_id'] = int(log['filter_id'])
            logging.info('{} {} {} {} {}'.format(
                log['timestamp'], log['id'], log['user'], log['filter'], len(log['details'])))

            for module in modules:
                try:
                    module(M, log)
                except Exception as e:
                    traceback.print_exc()
                    M.error(traceback.format_exc())

        if len(res["query"]["abuselog"]) > 0:
            timestamp = res["query"]["abuselog"][-1]["timestamp"]
            timestamp = int2tz(tz2int(timestamp) + 1)

    except Exception as e:
        traceback.print_exc()
        M.error(traceback.format_exc())

    time.sleep(20)
