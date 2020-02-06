# -*- coding: utf-8 -*-
import argparse
import datetime
import json
import logging
import os
import socket
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
parser.add_argument('--sleep', type=int, default=60)
parser.add_argument('-d', '--debug', action='store_const', dest='loglevel', const=logging.DEBUG)
parser.set_defaults(loglevel=logging.INFO)
args = parser.parse_args()

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)) + "/action")

logging.basicConfig(level=args.loglevel,
                    format='%(asctime)s {: <15} [%(filename)25s:%(lineno)4s] %(levelname)7s %(message)s'.format(args.wiki))

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

session = requests.Session()
session.headers.update({'User-Agent': M.wp_user_agent})


def int2tz(timeint):
    return (datetime.datetime.fromtimestamp(timeint, tz=pytz.utc)
            .isoformat().replace('+00:00', 'Z'))


def tz2int(timetz):
    return int(dateutil.parser.parse(timetz).timestamp())


timestamp = int2tz(int(time.time()))

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect((SOCKET_HOST, SOCKET_PORT))
logging.info('My address is {}'.format(sock.getsockname()))

while True:
    try:
        logging.debug('query {}'.format(timestamp))

        params = {
            'action': 'query',
            'format': 'json',
            'list': 'logevents',
            'lestart': timestamp,
            'ledir': 'newer',
            'leprop': 'ids|title|type|user|timestamp|comment|details|userid|parsedcomment',
            'lelimit': '500',
            'leaction': 'newusers/autocreate'
        }
        res = session.get(M.wp_api, params=params).json()

        if 'error' in res:
            logging.error('{}'.format(res['error']))
            M.error(res['error'])

        if 'query' not in res:
            logging.info('{}'.format(res))
            time.sleep(args.sleep)
            continue

        for log in res['query']['logevents']:
            change = {
                'id': None,
                'user': log['user'],
                'title': log['title'],
                'timestamp': tz2int(log['timestamp']),
                'wiki': args.wiki,
                'meta': {
                    'domain': domain,
                },
                'type': 'log',
                'namespace': log['ns'],
                'comment': log['comment'],
                'bot': False,
                'log_id': log['logid'],
                'log_type': log['type'],
                'log_action': log['action'],
                'log_params': {
                    'userid': log['params']['userid']
                },
                'log_action_comment': log['comment'],
                'parsedcomment': log['parsedcomment']
            }

            data = json.dumps(change)
            data = data.encode('utf-8')
            try:
                sock.sendall(data)
            except Exception as e:
                msg = 'Send {} bytes failed. {}'.format(len(data), e)
                logging.error(msg)
                M.error(msg)

        if len(res['query']['logevents']) > 0:
            timestamp = res['query']['logevents'][-1]['timestamp']
            timestamp = int2tz(tz2int(timestamp) + 1)

    except Exception as e:
        traceback.print_exc()
        M.error(traceback.format_exc())

    time.sleep(args.sleep)
