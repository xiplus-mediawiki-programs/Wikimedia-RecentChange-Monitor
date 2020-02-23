# -*- coding: utf-8 -*-
import argparse
import logging
import os
import socket
import traceback

from Monitor import Monitor, MonitorLogHandler
from rc_config import SOCKET_HOST, SOCKET_PORT
from sseclient import SSEClient as EventSource
from rc import process


parser = argparse.ArgumentParser()
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

url = 'https://stream.wikimedia.org/v2/stream/recentchange'

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect((SOCKET_HOST, SOCKET_PORT))
logging.info('My address is {}'.format(sock.getsockname()))

errorWaitTime = 1
while True:
    try:
        for event in EventSource(url):
            if event.event == 'message':
                if len(event.data) == 0:
                    continue

                logging.debug(event.data)

                noError = True

                data = event.data.encode('utf-8')
                process(data)

    except Exception as e:
        traceback.print_exc()
        M.error(traceback.format_exc(), noRaise=True)
