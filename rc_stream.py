# -*- coding: utf-8 -*-
import argparse
import json
import logging
import multiprocessing
import os
import socket
import time
import traceback
from datetime import datetime, timezone

from sseclient import SSEClient as EventSource

from Monitor import Monitor, MonitorLogHandler
from rc import process
from rc_config import SOCKET_HOST, SOCKET_PORT

parser = argparse.ArgumentParser()
parser.add_argument('--sleep', type=int, default=60)
parser.add_argument('--timeout', type=int, default=900)
parser.add_argument('-d', '--debug', action='store_const', dest='loglevel', const=logging.DEBUG)
parser.add_argument('-v', '--verbose', action='store_const', dest='loglevel', const=logging.INFO)
parser.set_defaults(loglevel=logging.WARNING)
args = parser.parse_args()
print(args)

logging.basicConfig(level=args.loglevel,
                    format='%(asctime)s [%(filename)20s:%(lineno)4s] %(levelname)7s %(message)s')

M = Monitor()

logging.getLogger().addHandler(MonitorLogHandler(M, 'allwiki'))

os.environ['TZ'] = 'UTC'

URL = 'https://stream.wikimedia.org/v2/stream/recentchange'

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect((SOCKET_HOST, SOCKET_PORT))
logging.info('My address is {}'.format(sock.getsockname()))

headers = {
    'User-Agent': M.wp_user_agent,
}


def main(lastOffset):
    fullUrl = URL
    if lastOffset.value > 0:
        fullUrl += '?since={}'.format(datetime.fromtimestamp(lastOffset.value, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    for event in EventSource(fullUrl, headers=headers):
        if event.event == 'message':
            if len(event.data) == 0:
                continue

            logging.debug(event.data)

            try:
                change = json.loads(event.data)
            except json.decoder.JSONDecodeError as e:
                msg = 'UnicodeDecodeError: {}. {}'.format(e, event.data)
                logging.error(msg)
                continue
            process(change)
            lastOffset.value = int(change['timestamp'])


lastOffset = multiprocessing.Value('i', 0)
while True:
    try:
        print('Last-Event-ID', lastOffset.value)
        p = multiprocessing.Process(target=main, args=(lastOffset,))
        p.start()
        p.join(timeout=args.timeout)

        if p.is_alive():
            p.terminate()
            p.join()

    except Exception as e:
        traceback.print_exc()
        M.error(traceback.format_exc(), noRaise=True)

        time.sleep(args.sleep)
