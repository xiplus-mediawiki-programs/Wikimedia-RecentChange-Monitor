# -*- coding: utf-8 -*-
import argparse
import datetime
import getpass
import json
import logging
import os
import pickle
import socket
import struct
import sys
import time
import traceback

import dateutil.parser
import pytz
import requests

from Monitor import Monitor, MonitorLogHandler
from rc_config import SOCKET_HOST, SOCKET_PORT

parser = argparse.ArgumentParser()
parser.add_argument('wiki', nargs='?', default='zhwiki')
parser.add_argument('--user')
parser.add_argument('--password')
parser.add_argument('--sleep', type=int, default=20)
parser.add_argument('--hidden', action='store_true')
parser.add_argument('-d', '--debug', action='store_const', dest='loglevel', const=logging.DEBUG)
parser.add_argument('-v', '--verbose', action='store_const', dest='loglevel', const=logging.INFO)
parser.set_defaults(
    hidden=False,
    loglevel=logging.WARNING,
)
args = parser.parse_args()
print(args)

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)) + "/action")

logging.basicConfig(level=args.loglevel,
                    format='%(asctime)s {: <15} [%(filename)20s:%(lineno)4s] %(levelname)7s %(message)s'.format(args.wiki))

M = Monitor()

logging.getLogger().addHandler(MonitorLogHandler(M, args.wiki))

os.environ['TZ'] = 'UTC'

M = Monitor()

M.db_execute("""SELECT `server_name` FROM `RC_wiki` WHERE `wiki` = %s""", (args.wiki))
domain = M.db_fetchone()
if domain is None:
    logging.error('Cannot get domain')
    exit()
else:
    domain = domain[0]
    logging.debug('domain is {}'.format(domain))

M.change_wiki_and_domain(args.wiki, domain)

api = 'https://{}/w/api.php'.format(domain)

if args.user:
    M.wp_user = args.user
    M.wp_pass = ''


# login to wikimedia

session = requests.Session()
session.headers.update({'User-Agent': M.wp_user_agent})

try:
    with open('cookie.txt', 'rb') as f:
        cookies = pickle.load(f)
        session.cookies = cookies
except Exception as e:
    logging.info("parse cookie file fail")

logging.debug("checking is logged in")
params = {'action': 'query', 'assert': 'user', 'assertuser': M.wp_user, 'format': 'json'}
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

    if args.user:
        if args.password is not None:
            M.wp_pass = args.password
        else:
            M.wp_pass = getpass.getpass('Password:')

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
        logging.error("log in fail: {}".format(res))
        exit()

else:
    logging.debug("logged in")

with open('cookie.txt', 'wb') as f:
    pickle.dump(session.cookies, f)


def int2tz(timeint):
    return (datetime.datetime.fromtimestamp(timeint, tz=pytz.utc)
            .isoformat().replace('+00:00', 'Z'))


def tz2int(timetz):
    return int(dateutil.parser.parse(timetz).timestamp())


timestamp = int2tz(int(time.time()))

aflprop = 'ids|user|title|action|result|timestamp|revid|filter'
if args.hidden:
    aflprop += '|hidden'
    logging.info('Include hidden log')

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect((SOCKET_HOST, SOCKET_PORT))
logging.info('My address is {}'.format(sock.getsockname()))

while True:
    try:
        logging.debug('query {}'.format(timestamp))

        params = {
            'action': 'query',
            'list': 'abuselog',
            'aflstart': timestamp,
            'aflprop': aflprop,
            'afldir': 'newer',
            'afllimit': '500',
            'format': 'json'
        }
        res = session.get(M.wp_api, params=params).json()

        if 'error' in res:
            logging.error('{}'.format(res['error']))
            M.error(res['error'])

        if 'query' not in res:
            logging.info('{}'.format(res))
            time.sleep(args.sleep)
            continue

        for log in res["query"]["abuselog"]:
            if log['filter_id'] == '':
                log['filter_id'] = M.get_af_id_by_name(log['filter'], args.wiki)

            if log['filter_id'].startswith('global-'):
                log['filter_id'] = int(log['filter_id'][7:])
                log['global'] = True
            else:
                log['filter_id'] = int(log['filter_id'])
                log['global'] = False

            log['wiki'] = args.wiki
            log['type'] = 'abuselog'
            log['meta'] = {
                'domain': domain
            }

            logging.debug('{} {} {} {} {} {}'.format(
                log['timestamp'], log['wiki'], log['id'], log['user'], log['filter_id'], log['filter']))

            data = json.dumps(log)
            data = data.encode('utf-8')
            length = struct.pack('>Q', len(data))
            try:
                sock.sendall(length)
                sock.sendall(data)
            except Exception as e:
                msg = 'Send {} bytes failed. {}'.format(len(data), e)
                logging.error(msg)
                M.error(msg)

        if len(res["query"]["abuselog"]) > 0:
            timestamp = res["query"]["abuselog"][-1]["timestamp"]
            timestamp = int2tz(tz2int(timestamp) + 1)

    except Exception as e:
        traceback.print_exc()
        M.error(traceback.format_exc())

    time.sleep(args.sleep)
